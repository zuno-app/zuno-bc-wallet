#!/usr/bin/env python3
"""
Test Circle SDK Setup

This script verifies that your Circle Developer-Controlled Wallets SDK
is properly configured and can communicate with Circle's API.
"""

import os
import sys


def test_setup():
    """Test that Circle SDK is properly configured"""

    print("=" * 70)
    print("Circle SDK Setup Test")
    print("=" * 70)
    print()

    # Check environment variables
    api_key = os.environ.get('CIRCLE_API_KEY')
    entity_secret = os.environ.get('CIRCLE_ENTITY_SECRET')

    print("1. Checking environment variables...")
    if not api_key:
        print("   ❌ CIRCLE_API_KEY not set")
        return False
    else:
        print(f"   ✓ CIRCLE_API_KEY set ({api_key[:8]}...)")

    if not entity_secret:
        print("   ❌ CIRCLE_ENTITY_SECRET not set")
        return False
    else:
        print(f"   ✓ CIRCLE_ENTITY_SECRET set ({len(entity_secret)} chars)")

    print()

    # Try to import Circle SDK
    print("2. Checking Circle SDK installation...")
    try:
        from circle.web3 import utils
        from circle.web3.developer_controlled_wallets import WalletSetsApi
        print("   ✓ Circle SDK imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import Circle SDK: {e}")
        print()
        print("Please install dependencies:")
        print("  uv sync")
        return False

    print()

    # Initialize client
    print("3. Initializing Circle SDK client...")
    try:
        client = utils.init_developer_controlled_wallets_client(
            api_key=api_key,
            entity_secret=entity_secret
        )
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False

    print()

    # Test API connection
    print("4. Testing API connection...")
    try:
        wallet_sets_api = WalletSetsApi(client)
        response = wallet_sets_api.list_wallet_sets()

        wallet_set_count = len(response.data.wallet_sets) if response.data.wallet_sets else 0
        print(f"   ✓ API connection successful")
        print(f"   ✓ Wallet sets found: {wallet_set_count}")

    except Exception as e:
        print(f"   ❌ API request failed: {e}")
        return False

    print()
    print("=" * 70)
    print()
    print("✅ SUCCESS! Circle SDK is properly configured.")
    print()
    print("Your setup is ready for wallet operations:")
    print("  • API Key: Validated")
    print("  • Entity Secret: Registered")
    print("  • SDK: Installed and working")
    print("  • API Connection: Active")
    print()
    print("You can now:")
    print("  1. Create wallet sets and wallets")
    print("  2. Send and receive transactions")
    print("  3. Query balances and transaction history")
    print()
    print("=" * 70)

    return True


def main():
    """Run the setup test"""
    try:
        success = test_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
