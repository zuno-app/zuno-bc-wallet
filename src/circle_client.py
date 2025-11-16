"""
Circle SDK client wrapper
Handles initialization and provides a clean interface to Circle's Developer-Controlled Wallets SDK
"""

import logging
from typing import Optional
from circle.web3 import utils
from circle.web3.developer_controlled_wallets import (
    WalletSetsApi,
    WalletsApi,
    TransactionsApi,
)

from .config import CircleConfig

logger = logging.getLogger(__name__)


class CircleClient:
    """Wrapper for Circle Developer-Controlled Wallets SDK"""

    def __init__(self, config: CircleConfig):
        """Initialize Circle SDK client"""
        self.config = config
        self._client = None
        self._wallet_sets_api: Optional[WalletSetsApi] = None
        self._wallets_api: Optional[WalletsApi] = None
        self._transactions_api: Optional[TransactionsApi] = None

    def initialize(self):
        """Initialize the Circle SDK client with API key and entity secret"""
        logger.info("Initializing Circle SDK client...")

        try:
            # Initialize the Circle SDK client
            self._client = utils.init_developer_controlled_wallets_client(
                api_key=self.config.api_key,
                entity_secret=self.config.entity_secret,
            )

            # Initialize API instances
            self._wallet_sets_api = WalletSetsApi(self._client)
            self._wallets_api = WalletsApi(self._client)
            self._transactions_api = TransactionsApi(self._client)

            logger.info("✓ Circle SDK client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Circle SDK client: {e}")
            raise

    @property
    def wallet_sets(self) -> WalletSetsApi:
        """Get Wallet Sets API"""
        if not self._wallet_sets_api:
            raise RuntimeError("Circle client not initialized. Call initialize() first.")
        return self._wallet_sets_api

    @property
    def wallets(self) -> WalletsApi:
        """Get Wallets API"""
        if not self._wallets_api:
            raise RuntimeError("Circle client not initialized. Call initialize() first.")
        return self._wallets_api

    @property
    def transactions(self) -> TransactionsApi:
        """Get Transactions API"""
        if not self._transactions_api:
            raise RuntimeError("Circle client not initialized. Call initialize() first.")
        return self._transactions_api

    async def health_check(self) -> bool:
        """Check if Circle API is accessible"""
        try:
            # Try to list wallet sets as a health check
            response = self.wallet_sets.list_wallet_sets()
            return True
        except Exception as e:
            logger.error(f"Circle API health check failed: {e}")
            return False


# Global client instance
_circle_client: Optional[CircleClient] = None


def get_circle_client() -> CircleClient:
    """Get or initialize the global Circle client"""
    global _circle_client
    if _circle_client is None:
        raise RuntimeError("Circle client not initialized. Call init_circle_client() first.")
    return _circle_client


def init_circle_client(config: CircleConfig) -> CircleClient:
    """Initialize the global Circle client"""
    global _circle_client
    if _circle_client is None:
        _circle_client = CircleClient(config)
        _circle_client.initialize()
    return _circle_client
