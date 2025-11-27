"""
Migration script to add password_hash column to employees table
This script adds the password_hash field and sets a default password for existing employees
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.auth import get_password_hash
from app.models import Employee


def migrate_add_password_hash():
    """Add password_hash column to employees table"""
    print("="*60)
    print("Migration: Adding password_hash to employees table")
    print("="*60)

    db = SessionLocal()

    try:
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='employees' AND column_name='password_hash'
            """))

            if result.fetchone():
                print("[OK] Column 'password_hash' already exists. Skipping migration.")
                return

        print("\n[1/2] Adding password_hash column...")

        # Add the column
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE employees
                ADD COLUMN password_hash VARCHAR(255)
            """))

        print("[OK] Column added successfully")

        print("\n[2/2] Setting default password for existing employees...")

        # Get all employees without password_hash
        employees = db.query(Employee).all()

        if not employees:
            print("[INFO] No existing employees found")
        else:
            # Set default password "password123" for all existing employees
            default_password_hash = get_password_hash("password123")

            for employee in employees:
                employee.password_hash = default_password_hash

            db.commit()

            print(f"[OK] Updated {len(employees)} employees with default password")
            print("\n[WARNING] IMPORTANT: Default password is 'password123'")
            print("          Users should change their password after first login!")

        print("\n" + "="*60)
        print("[SUCCESS] Migration completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Error during migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    try:
        migrate_add_password_hash()
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
