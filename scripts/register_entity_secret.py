#!/usr/bin/env python3
"""
Register Entity Secret with Circle

This script registers your entity secret's public key with Circle's service.
This is required before you can create wallets.

Based on: https://developers.circle.com/wallets/dev-controlled/entity-secret-management
"""

import os
import sys
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on environment variables


def register_entity_secret():
    """Register the entity secret with Circle"""

    print("=" * 70)
    print("Circle Entity Secret Registration")
    print("=" * 70)
    print()

    # Load environment variables
    api_key = os.environ.get('CIRCLE_API_KEY')
    entity_secret = os.environ.get('CIRCLE_ENTITY_SECRET')

    # Validate environment
    if not api_key:
        print("❌ Error: CIRCLE_API_KEY not set in environment")
        print()
        print("Please set your Circle API key:")
        print("  export CIRCLE_API_KEY='your_api_key_here'")
        print()
        sys.exit(1)

    if not entity_secret:
        print("❌ Error: CIRCLE_ENTITY_SECRET not set in environment")
        print()
        print("Please set your entity secret:")
        print("  export CIRCLE_ENTITY_SECRET='your_entity_secret_here'")
        print()
        print("Or generate one:")
        print("  python scripts/generate_entity_secret.py")
        print()
        sys.exit(1)

    # Validate entity secret format (should be 64 hex characters for 32 bytes)
    if len(entity_secret) != 64:
        print(f"⚠️  Warning: Entity secret length is {len(entity_secret)} characters")
        print("   Expected: 64 hex characters (32 bytes)")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

    print("Initializing Circle SDK client...")
    print()

    try:
        # Import Circle SDK
        from circle.web3 import utils

        # Initialize client
        # The SDK automatically handles entity secret registration
        # when you initialize the client for the first time
        client = utils.init_developer_controlled_wallets_client(
            api_key=api_key,
            entity_secret=entity_secret
        )

        print("✓ Client initialized successfully")
        print("✓ Entity secret registered with Circle")
        print()
        print("=" * 70)
        print()
        print("SUCCESS! Your entity secret is now ready to use.")
        print()
        print("Next steps:")
        print("  1. Test the setup:")
        print("     python scripts/test_circle_setup.py")
        print()
        print("  2. Start implementing wallet functionality")
        print()
        print("=" * 70)

        return True

    except ImportError:
        print("❌ Error: Circle SDK not installed")
        print()
        print("Please install dependencies:")
        print("  cd zuno-bc-wallet")
        print("  source .venv/bin/activate")
        print("  uv sync")
        print()
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error during registration: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Verify your CIRCLE_API_KEY is correct")
        print("  2. Check your internet connection")
        print("  3. Ensure the entity secret is in hex format (64 characters)")
        print("  4. Visit https://console.circle.com/ to verify your account")
        print()
        sys.exit(1)


if __name__ == "__main__":
    register_entity_secret()
