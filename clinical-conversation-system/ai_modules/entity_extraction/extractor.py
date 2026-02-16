"""
Generate a secure secret key for JWT authentication
File: generate_secret_key.py

Usage:
    python generate_secret_key.py
"""

import secrets


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key

    Args:
        length: Length of the secret key (default: 32)

    Returns:
        URL-safe base64-encoded secret key
    """
    return secrets.token_urlsafe(length)


def main():
    """Generate and display a new secret key"""
    print("\n" + "=" * 60)
    print("SECRET KEY GENERATOR")
    print("=" * 60)

    # Generate secret key
    secret_key = generate_secret_key()

    print("\nYour new SECRET_KEY:")
    print("-" * 60)
    print(secret_key)
    print("-" * 60)

    print("\n📝 Instructions:")
    print("1. Copy the secret key above")
    print("2. Open your .env file")
    print("3. Replace the SECRET_KEY value with the generated key:")
    print(f"   SECRET_KEY={secret_key}")
    print("\n⚠️  IMPORTANT:")
    print("   - NEVER commit this key to Git")
    print("   - Use different keys for development and production")
    print("   - Keep your .env file secure")
    print("   - Generate a NEW key if you suspect compromise")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
