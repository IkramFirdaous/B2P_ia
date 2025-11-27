from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
from app.core.config import settings
from app.models import Employee, EmployeeTeam
from app.schemas.auth_schema import (
    UserLogin,
    UserRegister,
    Token,
    UserResponse,
    ChangePassword
)


router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(Employee).filter(Employee.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_employee = Employee(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        team_id=user_data.team_id
    )

    db.add(new_employee)
    db.flush()  # Ensure ID is available without committing

    if user_data.team_id:
        primary_team_link = EmployeeTeam(
            employee_id=new_employee.id,
            team_id=user_data.team_id,
            is_primary=True
        )
        db.add(primary_team_link)

    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: Employee = Depends(get_current_active_user)):
    return current_user


@router.post("/auth/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/auth/logout")
def logout(current_user: Employee = Depends(get_current_active_user)):
    return {"message": "Logged out successfully"}
