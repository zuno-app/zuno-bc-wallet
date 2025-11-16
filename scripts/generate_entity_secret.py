#!/usr/bin/env python3
"""
Generate a secure Entity Secret for Circle Developer-Controlled Wallets

This script generates a cryptographically secure 32-byte entity secret
that can be used with Circle's Developer-Controlled Wallets SDK.

SECURITY WARNING:
- This entity secret is the master key for ALL wallets in your system
- Store it securely (HSM, KMS, or secure vault)
- Never commit it to version control
- Back it up in multiple secure locations
- If lost, ALL wallets are permanently inaccessible
"""

import secrets
import base64


def generate_entity_secret():
    """Generate a secure 32-byte entity secret"""

    print("=" * 70)
    print("Circle Entity Secret Generator")
    print("=" * 70)
    print()
    print("Generating cryptographically secure 32-byte entity secret...")
    print()

    # Generate 32 random bytes
    entity_secret_bytes = secrets.token_bytes(32)

    # Convert to hex (most common format)
    entity_secret_hex = entity_secret_bytes.hex()

    # Also provide base64 encoding
    entity_secret_b64 = base64.b64encode(entity_secret_bytes).decode('utf-8')

    # Display results
    print("✓ Entity Secret Generated")
    print()
    print("-" * 70)
    print("HEX FORMAT (recommended for Circle SDK):")
    print("-" * 70)
    print(entity_secret_hex)
    print()
    print("-" * 70)
    print("BASE64 FORMAT (alternative):")
    print("-" * 70)
    print(entity_secret_b64)
    print()
    print("=" * 70)
    print()

    # Security warnings
    print("⚠️  SECURITY WARNINGS:")
    print()
    print("1. SAVE THIS VALUE IMMEDIATELY - it cannot be recovered")
    print("2. Store in a secure location (HSM, KMS, password manager)")
    print("3. Create encrypted backups in multiple secure locations")
    print("4. NEVER commit this to version control")
    print("5. NEVER share this value with anyone")
    print("6. Use different entity secrets for dev/staging/production")
    print("7. If compromised, ALL wallets must be migrated immediately")
    print()
    print("=" * 70)
    print()

    # Usage instructions
    print("USAGE:")
    print()
    print("1. Copy the HEX value above")
    print("2. Add it to your .env file:")
    print(f"   CIRCLE_ENTITY_SECRET={entity_secret_hex}")
    print()
    print("3. Register it with Circle:")
    print("   python scripts/register_entity_secret.py")
    print()
    print("=" * 70)

    return entity_secret_hex


if __name__ == "__main__":
    generate_entity_secret()
