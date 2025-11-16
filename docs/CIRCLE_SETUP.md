# Circle Developer-Controlled Wallets Setup Guide

This guide walks you through setting up Circle's Developer-Controlled Wallets SDK for the Zuno wallet application.

## Prerequisites

- Python 3.14+ installed
- Circle Developer Account
- Basic understanding of blockchain wallets

## Step 1: Create Circle Developer Account

1. Visit [Circle Developer Console](https://console.circle.com/)
2. Sign up for a Developer Account
3. Verify your email address
4. Complete the onboarding process

## Step 2: Get Your API Key

1. Log in to the [Circle Console](https://console.circle.com/)
2. Navigate to **API Keys** section
3. Click **Create API Key**
4. Give it a descriptive name (e.g., "Zuno Wallet Development")
5. **Important**: Copy and securely store your API key immediately - you won't be able to see it again
6. Add the API key to your `.env` file:
   ```bash
   CIRCLE_API_KEY=your_api_key_here
   ```

## Step 3: Generate Entity Secret

The Entity Secret is your master encryption key for all wallets. **Circle never stores this** - you must keep it secure.

### What is an Entity Secret?

- A 32-byte (256-bit) cryptographic key
- Used to derive all wallet keys in your system
- **CRITICAL**: If you lose this, you lose access to ALL wallets
- Should be stored in a Hardware Security Module (HSM) or secure key management system in production

### Generate Entity Secret

You can generate the Entity Secret using Python:

```python
import secrets

# Generate a secure 32-byte entity secret
entity_secret = secrets.token_hex(32)
print(f"Entity Secret (hex): {entity_secret}")

# Or as base64
import base64
entity_secret_bytes = secrets.token_bytes(32)
entity_secret_b64 = base64.b64encode(entity_secret_bytes).decode('utf-8')
print(f"Entity Secret (base64): {entity_secret_b64}")
```

**Save this value immediately in a secure location!**

## Step 4: Register Entity Secret with Circle

Before you can use the Entity Secret, you must register its public key with Circle.

### 4.1 Install Dependencies

```bash
cd zuno-bc-wallet
source .venv/bin/activate
uv sync
```

### 4.2 Create Registration Script

Create a file `scripts/register_entity_secret.py`:

```python
"""
Script to register Entity Secret with Circle
Based on: https://developers.circle.com/wallets/dev-controlled/entity-secret-management
"""

import os
import sys
from circle.web3 import utils
from circle.web3.developer_controlled_wallets import EntitySecretCiphertext

def register_entity_secret():
    """Register the entity secret with Circle"""

    # Load environment variables
    api_key = os.environ.get('CIRCLE_API_KEY')
    entity_secret = os.environ.get('CIRCLE_ENTITY_SECRET')

    if not api_key:
        print("Error: CIRCLE_API_KEY not set in environment")
        sys.exit(1)

    if not entity_secret:
        print("Error: CIRCLE_ENTITY_SECRET not set in environment")
        sys.exit(1)

    print("Initializing Circle SDK client...")

    try:
        # Initialize client
        client = utils.init_developer_controlled_wallets_client(
            api_key=api_key,
            entity_secret=entity_secret
        )

        print("✓ Client initialized successfully")

        # The SDK handles entity secret registration automatically
        # when you initialize the client
        print("✓ Entity secret registered with Circle")
        print("")
        print("Your entity secret is now ready to use!")
        print("You can now create wallets using this entity secret.")

    except Exception as e:
        print(f"Error during registration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    register_entity_secret()
```

### 4.3 Run Registration

```bash
# Set your environment variables
export CIRCLE_API_KEY="your_api_key_here"
export CIRCLE_ENTITY_SECRET="your_entity_secret_here"

# Run the registration script
python scripts/register_entity_secret.py
```

You should see:
```
✓ Client initialized successfully
✓ Entity secret registered with Circle

Your entity secret is now ready to use!
You can now create wallets using this entity secret.
```

## Step 5: Verify Setup

Create a test script `scripts/test_circle_setup.py`:

```python
"""Test Circle SDK setup"""

import os
from circle.web3 import utils
from circle.web3.developer_controlled_wallets import WalletSetsApi

def test_setup():
    """Test that Circle SDK is properly configured"""

    api_key = os.environ.get('CIRCLE_API_KEY')
    entity_secret = os.environ.get('CIRCLE_ENTITY_SECRET')

    if not api_key or not entity_secret:
        print("Error: Environment variables not set")
        return False

    try:
        # Initialize client
        client = utils.init_developer_controlled_wallets_client(
            api_key=api_key,
            entity_secret=entity_secret
        )

        # Try to list wallet sets (should return empty list for new account)
        wallet_sets_api = WalletSetsApi(client)
        response = wallet_sets_api.list_wallet_sets()

        print("✓ Circle SDK setup successful!")
        print(f"  API connection: OK")
        print(f"  Entity secret: OK")
        print(f"  Wallet sets: {len(response.data.wallet_sets)}")

        return True

    except Exception as e:
        print(f"✗ Setup test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_setup()
    exit(0 if success else 1)
```

Run the test:
```bash
python scripts/test_circle_setup.py
```

## Step 6: Update .env File

Create your `.env` file from the template:

```bash
cp .env.template .env
```

Edit `.env` and add your credentials:

```bash
# Circle API credentials
CIRCLE_API_KEY=your_actual_api_key_here
CIRCLE_ENTITY_SECRET=your_actual_entity_secret_here

# Network configuration
DEFAULT_BLOCKCHAIN=ARC-TESTNET
SUPPORTED_BLOCKCHAINS=ARC-TESTNET,MATIC-AMOY,ARB-SEPOLIA

# Service configuration
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
SERVICE_ENV=development
```

## Supported Blockchain Networks

Circle supports multiple blockchain networks. Here are the common ones:

### Testnets (for development)
- `ARC-TESTNET` - Arc testnet
- `MATIC-AMOY` - Polygon Amoy testnet
- `ARB-SEPOLIA` - Arbitrum Sepolia testnet
- `ETH-SEPOLIA` - Ethereum Sepolia testnet
- `AVAX-FUJI` - Avalanche Fuji testnet
- `SOL-DEVNET` - Solana devnet

### Mainnets (for production)
- `ARC-MAINNET` - Arc mainnet
- `MATIC-MAINNET` - Polygon mainnet
- `ARB-MAINNET` - Arbitrum One mainnet
- `ETH-MAINNET` - Ethereum mainnet
- `AVAX-MAINNET` - Avalanche C-Chain mainnet
- `SOL-MAINNET` - Solana mainnet

Check [Circle's documentation](https://developers.circle.com/wallets/dev-controlled/supported-blockchains) for the latest supported networks.

## Security Best Practices

### Development Environment

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use separate API keys** for development and production
3. **Rotate API keys regularly**
4. **Use different Entity Secrets** for dev/staging/production
5. **Store Entity Secret** in environment variables, never in code

### Production Environment

1. **Use HSM** (Hardware Security Module) for Entity Secret storage
2. **Enable API key rotation** with multiple keys
3. **Implement key backup** strategy with secure, offline storage
4. **Use secrets management** service (AWS Secrets Manager, HashiCorp Vault, etc.)
5. **Enable audit logging** for all wallet operations
6. **Set up monitoring** and alerts for suspicious activity
7. **Implement rate limiting** to prevent abuse
8. **Use IP whitelisting** if possible

### Entity Secret Backup

The Entity Secret is the master key to all wallets. If lost, all wallets are irrecoverable.

**Backup Strategy**:
1. **Primary**: Store in production HSM
2. **Backup 1**: Encrypted offline storage in secure physical location
3. **Backup 2**: Split key shares using Shamir's Secret Sharing across multiple trusted parties
4. **Document**: Clear recovery procedures

Example Shamir's Secret Sharing (for backup only):

```python
# Using 'secretsharing' library
from secretsharing import PlaintextToHexSecretSharer

# Split entity secret into 5 shares, requiring 3 to reconstruct
shares = PlaintextToHexSecretSharer.split_secret(
    entity_secret,
    threshold=3,
    share_count=5
)

# Distribute shares to 5 different secure locations
# Any 3 shares can reconstruct the original secret
```

## Troubleshooting

### Error: "Invalid API key"

- Verify your API key is correct
- Check if the API key has been revoked
- Ensure you're using the right environment (testnet vs mainnet)

### Error: "Entity secret not registered"

- Run the registration script again
- Verify the entity secret format is correct (64 hex characters for 32 bytes)
- Check Circle Console for entity secret status

### Error: "Network not supported"

- Check the blockchain identifier spelling
- Verify your Circle account has access to that network
- See [supported blockchains](https://developers.circle.com/wallets/dev-controlled/supported-blockchains)

### Error: "Rate limit exceeded"

- Implement exponential backoff in your code
- Consider caching wallet data
- Upgrade your Circle plan if needed

## Next Steps

Once setup is complete:

1. ✓ Circle account created
2. ✓ API key obtained
3. ✓ Entity secret generated and registered
4. ✓ Environment configured
5. → Proceed to implement WalletService in `main.py`

## Resources

- [Circle Developer Documentation](https://developers.circle.com/wallets/dev-controlled)
- [Circle Python SDK Reference](https://developers.circle.com/sdk-explorer/developer-controlled-wallets/Python)
- [Entity Secret Management](https://developers.circle.com/wallets/dev-controlled/entity-secret-management)
- [Circle Console](https://console.circle.com/)
- [Circle Support](https://support.circle.com/)
