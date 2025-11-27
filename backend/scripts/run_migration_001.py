"""
Migration Script: Add Multi-Team Support
Run this script to apply database schema changes for many-to-many Employee-Team relationship
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base, Employee, Team, EmployeeTeam, Task

def run_migration():
    """Execute the migration to add multi-team support"""

    print("🚀 Starting Migration: Add Multi-Team Support")
    print("=" * 60)

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Read the SQL migration file
        migration_file = Path(__file__).parent.parent / "migrations" / "001_add_multi_team_support.sql"

        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False

        print(f"📄 Reading migration from: {migration_file}")

        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Split by parts (each part is separated by -- ====)
        parts = migration_sql.split('-- ============================================================================')

        print("\n📋 Migration Steps:")
        print("  1. Create employee_teams junction table")
        print("  2. Migrate existing employee-team relationships")
        print("  3. Add difficulty and team_id to tasks")
        print("  4. Add ASSIGNED to TaskSource enum")
        print("  5. Update existing data")

        # Ask for confirmation
        print("\n⚠️  WARNING: This will modify your database schema!")
        confirmation = input("\nProceed with migration? (yes/no): ").strip().lower()

        if confirmation != 'yes':
            print("\n❌ Migration cancelled by user")
            return False

        print("\n🔄 Executing migration...")

        # Execute the full migration
        # Note: We execute the whole file at once, but you could split it
        # into individual statements if needed for better error handling

        with engine.connect() as connection:
            # Execute within a transaction
            trans = connection.begin()
            try:
                # Parse SQL file more carefully to handle DO blocks
                lines = migration_sql.split('\n')
                current_statement = []
                in_do_block = False
                in_comment_block = False

                for line in lines:
                    # Track comment blocks
                    if '/*' in line:
                        in_comment_block = True
                    if '*/' in line:
                        in_comment_block = False
                        continue

                    # Skip comments and verification sections
                    if in_comment_block or line.strip().startswith('--'):
                        continue
                    if 'VERIFICATION' in line.upper() or 'ROLLBACK' in line.upper():
                        break

                    # Track DO blocks (they use $$ delimiters)
                    if 'DO $$' in line.upper():
                        in_do_block = True

                    current_statement.append(line)

                    # Execute statement when we hit a semicolon
                    if line.strip().endswith(';'):
                        # Check if this is the end of a DO block
                        if in_do_block and 'END $$' in line.upper():
                            in_do_block = False
                            # Execute the complete DO block
                            stmt = '\n'.join(current_statement).strip()
                            if stmt:
                                print(f"  ⏳ Executing DO block...")
                                connection.execute(text(stmt))
                            current_statement = []
                        elif not in_do_block:
                            # Execute regular statement
                            stmt = '\n'.join(current_statement).strip()
                            if stmt and len(stmt) > 3:  # Avoid empty statements
                                # Show truncated version for display
                                display_stmt = stmt.replace('\n', ' ').strip()[:60]
                                print(f"  ⏳ Executing: {display_stmt}...")
                                connection.execute(text(stmt))
                            current_statement = []

                trans.commit()
                print("\n✅ Migration executed successfully!")

            except Exception as e:
                trans.rollback()
                print(f"\n❌ Migration failed: {str(e)}")
                print("\nRolling back changes...")
                raise

        # Verify the migration
        print("\n🔍 Verifying migration...")

        with engine.connect() as connection:
            # Check employee_teams table exists
            result = connection.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'employee_teams'
            """))
            if result.scalar() == 1:
                print("  ✅ employee_teams table created")
            else:
                print("  ❌ employee_teams table not found")

            # Count employee-team relationships
            result = connection.execute(text("SELECT COUNT(*) FROM employee_teams"))
            count = result.scalar()
            print(f"  ✅ {count} employee-team relationships migrated")

            # Check tasks have difficulty field
            result = connection.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'difficulty'
            """))
            if result.scalar() == 1:
                print("  ✅ tasks.difficulty field added")
            else:
                print("  ❌ tasks.difficulty field not found")

            # Check tasks have team_id field
            result = connection.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'tasks' AND column_name = 'team_id'
            """))
            if result.scalar() == 1:
                print("  ✅ tasks.team_id field added")
            else:
                print("  ❌ tasks.team_id field not found")

            # Check ASSIGNED enum value
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_enum
                    WHERE enumlabel = 'assigned'
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'tasksource')
                )
            """))
            if result.scalar():
                print("  ✅ ASSIGNED added to TaskSource enum")
            else:
                print("  ❌ ASSIGNED not found in TaskSource enum")

        print("\n" + "=" * 60)
        print("🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Restart your backend server")
        print("  2. Test the multi-team functionality")
        print("  3. Verify all existing data is intact")
        print("\nTo rollback, see the ROLLBACK section in the SQL file")

        return True

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
