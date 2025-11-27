"""
Generate a secure random SECRET_KEY for JWT authentication
Run this script and copy the output to your .env file
"""
import secrets

def generate_secret_key(length=64):
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("\n" + "="*70)
    print("Generated SECRET_KEY for JWT Authentication")
    print("="*70)
    print(f"\nSECRET_KEY={secret_key}\n")
    print("="*70)
    print("\nCopy the line above and add it to your backend/.env file")
    print("Keep this key secret and never commit it to version control!\n")

