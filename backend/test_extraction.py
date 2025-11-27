"""Test email extraction with fresh email"""
from app.core.database import get_db
from app.models import EmailCredential
from app.services.email_extraction_service import EmailExtractionService

db = next(get_db())

# Get email credential
cred = db.query(EmailCredential).first()
if not cred:
    print("ERROR: No email credentials found!")
    exit(1)

print(f"Testing email extraction for: {cred.email_address}")

# Process emails
service = EmailExtractionService(db)
try:
    result = service.process_emails(
        employee_id=cred.employee_id,
        max_emails=3,
        unread_only=False
    )

    print("\n=== RESULTS ===")
    print(f"Fetched: {result['emails_fetched']}")
    print(f"Processed: {result['emails_processed']}")
    print(f"Failed: {result['emails_failed']}")
    print(f"Tasks extracted: {result['tasks_extracted']}")

    if result['errors']:
        print("\nERRORS:")
        for err in result['errors']:
            print(f"  - {err}")

    if result['tasks_extracted'] > 0:
        print("\n✓ SUCCESS! Tasks were extracted from emails!")
    elif result['emails_processed'] == 0 and result['emails_failed'] == 0:
        print("\nℹ All emails already processed (duplicates skipped)")
    elif result['emails_failed'] > 0:
        print("\n✗ FAILED! Check errors above")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
