# Phase 1: Database Models - ✅ COMPLETE

## Summary

Phase 1 of the multi-team and wellbeing system implementation is now complete! All database models have been updated to support the new architecture.

---

## What Was Implemented

### 1. ✅ Many-to-Many Employee ↔ Team Relationship

**New Model Created**: `EmployeeTeam` ([employee_team.py](backend/app/models/employee_team.py))

```python
class EmployeeTeam(BaseModel):
    employee_id: UUID
    team_id: UUID
    joined_at: DateTime
    is_primary: Boolean  # Mark one team as primary
```

**Benefits**:
- Employees can now belong to multiple teams simultaneously
- Each employee can have one primary team
- Tracks when employees joined each team

### 2. ✅ Updated Employee Model

**File**: [backend/app/models/employee.py](backend/app/models/employee.py)

**Changes**:
- ❌ Removed: `team_id` column (single team)
- ✅ Added: `employee_teams` relationship (junction table)
- ✅ Added: `teams` relationship (easy access via secondary)

**Before**:
```python
team_id = Column(UUID, ForeignKey("teams.id"))
team = relationship("Team", back_populates="members")
```

**After**:
```python
employee_teams = relationship("EmployeeTeam", back_populates="employee")
teams = relationship("Team", secondary="employee_teams", back_populates="members")
```

### 3. ✅ Updated Team Model

**File**: [backend/app/models/team.py](backend/app/models/team.py)

**Changes**:
- ❌ Removed: Direct `members` relationship
- ✅ Added: `team_employees` relationship (junction table)
- ✅ Added: `members` relationship (easy access via secondary)
- ✅ Added: `tasks` relationship (one-to-many with tasks)

**New Capability**: Teams can now have tasks associated with them

### 4. ✅ Enhanced Task Model

**File**: [backend/app/models/task.py](backend/app/models/task.py)

**New Fields**:
1. **`difficulty`** (Integer 1-5): Task complexity level
2. **`team_id`** (UUID): Associate task with a team
3. **`ASSIGNED`** source type: New TaskSource enum value

**Before**:
```python
class TaskSource(str, enum.Enum):
    EMAIL = "email"
    MEETING = "meeting"
    MANUAL = "manual"
    CALENDAR = "calendar"
```

**After**:
```python
class TaskSource(str, enum.Enum):
    EMAIL = "email"
    MEETING = "meeting"
    MANUAL = "manual"
    CALENDAR = "calendar"
    ASSIGNED = "assigned"  # ✅ NEW

class Task(BaseModel):
    # ... existing fields ...
    difficulty = Column(Integer, default=3)  # ✅ NEW (1-5 scale)
    team_id = Column(UUID, ForeignKey("teams.id"))  # ✅ NEW
```

### 5. ✅ Database Migration Scripts

**Created Two Migration Approaches**:

#### A. SQL Migration Script
**File**: [backend/migrations/001_add_multi_team_support.sql](backend/migrations/001_add_multi_team_support.sql)

- Comprehensive SQL script with 7 parts
- Includes data migration from old schema to new
- Verification queries included
- Rollback script provided
- Can be run directly in PostgreSQL

#### B. Python Migration Script
**File**: [backend/scripts/run_migration_001.py](backend/scripts/run_migration_001.py)

- Automated migration execution
- Confirmation prompts before execution
- Transaction support (auto-rollback on error)
- Verification checks after migration
- User-friendly progress messages

**To run**:
```bash
cd backend
python scripts/run_migration_001.py
```

---

## Database Schema Changes

### Tables Created
- `employee_teams` - Junction table for many-to-many relationship

### Tables Modified
- `employees` - Removed `team_id` column
- `tasks` - Added `difficulty` and `team_id` columns

### Enum Types Modified
- `tasksource` - Added `assigned` value

### Indexes Created
- `idx_employee_teams_employee_id`
- `idx_employee_teams_team_id`
- `idx_tasks_team_id`

---

## Data Migration Strategy

The migration automatically handles existing data:

1. **Existing Employee-Team Relationships**:
   - All existing `team_id` values from `employees` are migrated to `employee_teams`
   - These are marked as `is_primary = TRUE` (primary team)
   - The original `team_id` column is then removed

2. **Existing Tasks**:
   - All tasks get `difficulty = 3` (medium) by default
   - Tasks are associated with their creator's primary team
   - Existing source types remain unchanged

3. **Zero Downtime**:
   - The migration preserves all existing relationships
   - No data loss
   - Rollback script available if needed

---

## How to Apply the Migration

### Option 1: Automated Python Script (Recommended)

```bash
cd backend
python scripts/run_migration_001.py
```

This will:
- ✅ Show you what changes will be made
- ✅ Ask for confirmation
- ✅ Execute the migration in a transaction
- ✅ Verify all changes succeeded
- ✅ Rollback automatically if any error occurs

### Option 2: Manual SQL Execution

```bash
psql -U your_user -d your_database -f backend/migrations/001_add_multi_team_support.sql
```

---

## Verification Steps

After running the migration, verify with these queries:

### 1. Check employee_teams table exists
```sql
SELECT COUNT(*) FROM employee_teams;
```
Expected: Count of all employee-team relationships

### 2. Check employees with multiple teams
```sql
SELECT e.name, COUNT(et.team_id) as team_count
FROM employees e
JOIN employee_teams et ON e.id = et.employee_id
GROUP BY e.id, e.name
HAVING COUNT(et.team_id) > 1;
```

### 3. Check task difficulty distribution
```sql
SELECT difficulty, COUNT(*) as count
FROM tasks
GROUP BY difficulty
ORDER BY difficulty;
```

### 4. Check ASSIGNED source type
```sql
SELECT enumlabel FROM pg_enum
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tasksource');
```
Expected to include: `assigned`

---

## What's Next: Phase 2

Now that the database models are ready, the next phase is **Backend Services**:

### Phase 2 Tasks:

1. **Create WellbeingService** ([wellbeing_service.py](backend/app/services/wellbeing_service.py))
   - Calculate workload score
   - Calculate stress level
   - Detect task overlaps
   - Calculate burnout risk

2. **Create API Endpoints**:
   - `GET /api/v1/wellbeing/summary` - Complete wellbeing summary
   - `GET /api/v1/wellbeing/workload` - Workload score
   - `GET /api/v1/wellbeing/overlap-risks` - Deadline conflicts
   - `GET /api/v1/employees/{id}/teams` - Get employee's teams
   - `POST /api/v1/employees/{id}/teams/{team_id}` - Add employee to team
   - `PUT /api/v1/tasks` - Update to handle new fields (difficulty, team_id)

3. **Update Existing Endpoints**:
   - `GET /api/v1/tasks` - Add filters for team_id, source, difficulty
   - `POST /api/v1/tasks` - Accept difficulty and team_id
   - `GET /api/v1/teams/{id}/members` - Use new many-to-many relationship

---

## Files Created/Modified

### Created:
- ✅ `backend/app/models/employee_team.py`
- ✅ `backend/migrations/001_add_multi_team_support.sql`
- ✅ `backend/scripts/run_migration_001.py`

### Modified:
- ✅ `backend/app/models/employee.py`
- ✅ `backend/app/models/team.py`
- ✅ `backend/app/models/task.py`
- ✅ `backend/app/models/__init__.py`

---

## Rollback Instructions

If you need to revert the migration, see the ROLLBACK section in:
- [001_add_multi_team_support.sql](backend/migrations/001_add_multi_team_support.sql)

**WARNING**: Only rollback if absolutely necessary, as this will:
- Recreate the `team_id` column in employees
- Remove the `employee_teams` table
- Remove `difficulty` and `team_id` from tasks
- Employees will lose membership in all teams except their primary

---

## Testing Checklist

Before proceeding to Phase 2, verify:

- [ ] Migration script runs without errors
- [ ] employee_teams table exists with data
- [ ] employees.team_id column is removed
- [ ] tasks.difficulty column exists (default = 3)
- [ ] tasks.team_id column exists
- [ ] TaskSource enum includes 'assigned'
- [ ] All existing relationships are preserved
- [ ] Backend server starts without errors (import tests)

---

## Status: ✅ READY FOR PHASE 2

The database foundation is now ready for the wellbeing calculation services and API endpoints!

**Next Command**:
```bash
python scripts/run_migration_001.py
```

Then proceed to Phase 2: Backend Services implementation.

---

**Created**: 2025-11-26
**Phase**: 1 of 4 (Database Models)
**Status**: COMPLETE ✅
