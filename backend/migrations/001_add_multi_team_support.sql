-- Migration: Add Multi-Team Support and Wellbeing Fields
-- Date: 2025-11-26
-- Description: Transform Employee-Team relationship from one-to-many to many-to-many
--              Add difficulty and team_id to tasks
--              Add ASSIGNED source type

-- ============================================================================
-- PART 1: Create employee_teams junction table
-- ============================================================================

CREATE TABLE IF NOT EXISTS employee_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW() NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Unique constraint: an employee can't join the same team twice
    CONSTRAINT uq_employee_team UNIQUE (employee_id, team_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_employee_teams_employee_id ON employee_teams(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_teams_team_id ON employee_teams(team_id);

-- ============================================================================
-- PART 2: Migrate existing employee-team relationships
-- ============================================================================

-- Migrate all existing team_id from employees to employee_teams
-- Mark these as primary teams since they were the only team
INSERT INTO employee_teams (id, employee_id, team_id, is_primary, joined_at, created_at, updated_at)
SELECT
    gen_random_uuid(),
    id AS employee_id,
    team_id,
    TRUE AS is_primary,  -- Mark as primary team
    created_at AS joined_at,
    NOW() AS created_at,
    NOW() AS updated_at
FROM employees
WHERE team_id IS NOT NULL;

-- ============================================================================
-- PART 3: Remove team_id column from employees (after migration)
-- ============================================================================

-- WARNING: Only run this after verifying the migration succeeded!
-- Comment out if you want to keep team_id temporarily for safety

-- ALTER TABLE employees DROP COLUMN IF EXISTS team_id;

-- ============================================================================
-- PART 4: Add new fields to tasks table
-- ============================================================================

-- Add difficulty field (1-5 scale for task complexity)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS difficulty INTEGER DEFAULT 3 CHECK (difficulty >= 1 AND difficulty <= 5);

-- Add team_id field to associate tasks with teams
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id) ON DELETE SET NULL;

-- Create index for team-based task queries
CREATE INDEX IF NOT EXISTS idx_tasks_team_id ON tasks(team_id);

-- ============================================================================
-- PART 5: Add ASSIGNED to TaskSource enum
-- ============================================================================

-- Check if the enum value already exists, if not add it
DO $$
BEGIN
    -- Add 'assigned' to tasksource enum if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumlabel = 'assigned'
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tasksource')
    ) THEN
        ALTER TYPE tasksource ADD VALUE 'assigned';
    END IF;
END $$;

-- ============================================================================
-- PART 6: Update existing data (optional but recommended)
-- ============================================================================

-- Set difficulty to 3 (medium) for all existing tasks that don't have it
UPDATE tasks
SET difficulty = 3
WHERE difficulty IS NULL;

-- Associate existing tasks with their creator's primary team
UPDATE tasks t
SET team_id = (
    SELECT et.team_id
    FROM employee_teams et
    WHERE et.employee_id = t.created_by
    AND et.is_primary = TRUE
    LIMIT 1
)
WHERE t.team_id IS NULL
AND t.created_by IS NOT NULL;

-- ============================================================================
-- PART 7: Verification Queries (run these to verify migration success)
-- ============================================================================

-- Count of employee-team relationships
-- SELECT COUNT(*) as employee_team_count FROM employee_teams;

-- Employees with multiple teams
-- SELECT e.name, e.email, COUNT(et.team_id) as team_count
-- FROM employees e
-- JOIN employee_teams et ON e.id = et.employee_id
-- GROUP BY e.id, e.name, e.email
-- HAVING COUNT(et.team_id) > 1;

-- Tasks without team assignment
-- SELECT COUNT(*) as tasks_without_team FROM tasks WHERE team_id IS NULL;

-- Tasks by source type (should include 'assigned' after migration)
-- SELECT source, COUNT(*) as task_count
-- FROM tasks
-- GROUP BY source
-- ORDER BY task_count DESC;

-- Difficulty distribution
-- SELECT difficulty, COUNT(*) as task_count
-- FROM tasks
-- GROUP BY difficulty
-- ORDER BY difficulty;

-- ============================================================================
-- ROLLBACK SCRIPT (in case you need to revert)
-- ============================================================================

/*
-- ROLLBACK PART 1: Re-add team_id to employees
ALTER TABLE employees ADD COLUMN IF NOT EXISTS team_id UUID REFERENCES teams(id);

-- ROLLBACK PART 2: Restore team_id from primary team in employee_teams
UPDATE employees e
SET team_id = (
    SELECT et.team_id
    FROM employee_teams et
    WHERE et.employee_id = e.id
    AND et.is_primary = TRUE
    LIMIT 1
);

-- ROLLBACK PART 3: Drop employee_teams table
DROP INDEX IF EXISTS idx_employee_teams_employee_id;
DROP INDEX IF EXISTS idx_employee_teams_team_id;
DROP TABLE IF EXISTS employee_teams CASCADE;

-- ROLLBACK PART 4: Remove new task fields
DROP INDEX IF EXISTS idx_tasks_team_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS difficulty;
ALTER TABLE tasks DROP COLUMN IF EXISTS team_id;

-- ROLLBACK PART 5: Remove 'assigned' from enum (requires recreation)
-- NOTE: Removing enum values in PostgreSQL requires recreating the enum
-- This is complex and should be done carefully in production
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

-- Success message
SELECT 'Migration completed successfully! ✅' as status;
