"""
Wallet Service
Core business logic for wallet operations using Circle SDK
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from circle.web3.developer_controlled_wallets import (
    CreateWalletSetRequest,
    CreateWalletRequest,
    CreateDeveloperTransactionTransferRequest,
)

from .circle_client import get_circle_client
from .networks import get_network, is_supported_network
from .models import (
    CreateWalletRequest as CreateWalletRequestModel,
    WalletResponse,
    BalanceResponse,
    SendTransactionRequest,
    TransactionResponse,
)

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet operations"""

    def __init__(self):
        """Initialize wallet service"""
        self.client = get_circle_client()

    async def create_wallet(self, request: CreateWalletRequestModel) -> WalletResponse:
        """
        Create a new wallet for a user

        Args:
            request: Wallet creation request with user_id, blockchain, etc.

        Returns:
            WalletResponse with wallet details

        Raises:
            ValueError: If blockchain is not supported
            Exception: If wallet creation fails
        """
        logger.info(f"Creating wallet for user {request.user_id} on {request.blockchain}")

        # Validate blockchain
        if not is_supported_network(request.blockchain):
            raise ValueError(f"Unsupported blockchain: {request.blockchain}")

        network = get_network(request.blockchain)

        try:
            # Step 1: Create or get wallet set
            wallet_set_name = request.wallet_set_name or f"user-{request.user_id}-wallets"

            wallet_set_request = CreateWalletSetRequest.from_dict({
                "name": wallet_set_name
            })

            wallet_set_response = self.client.wallet_sets.create_wallet_set(wallet_set_request)
            wallet_set = wallet_set_response.data.wallet_set

            logger.info(f"✓ Wallet set created/retrieved: {wallet_set.id}")

            # Step 2: Create wallet in the wallet set
            create_wallet_request = CreateWalletRequest.from_dict({
                "idempotency_key": str(uuid.uuid4()),
                "wallet_set_id": wallet_set.id,
                "account_type": request.account_type,
                "blockchains": [request.blockchain],
                "count": 1,
            })

            wallet_response = self.client.wallets.create_wallet(create_wallet_request)
            wallet = wallet_response.data.wallets[0]

            logger.info(f"✓ Wallet created: {wallet.id}, address: {wallet.address}")

            return WalletResponse(
                wallet_id=wallet.id,
                wallet_set_id=wallet_set.id,
                address=wallet.address,
                blockchain=wallet.blockchain,
                account_type=wallet.account_type,
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            raise

    async def get_wallet(self, wallet_id: str) -> Optional[Dict]:
        """
        Get wallet details by ID

        Args:
            wallet_id: Circle wallet ID

        Returns:
            Wallet details dictionary or None if not found
        """
        try:
            response = self.client.wallets.get_wallet(wallet_id)
            wallet = response.data.wallet
            return {
                "wallet_id": wallet.id,
                "wallet_set_id": wallet.wallet_set_id,
                "address": wallet.address,
                "blockchain": wallet.blockchain,
                "account_type": wallet.account_type,
                "state": wallet.state,
            }
        except Exception as e:
            logger.error(f"Failed to get wallet {wallet_id}: {e}")
            return None

    async def get_balance(self, wallet_id: str) -> BalanceResponse:
        """
        Get wallet balance

        Args:
            wallet_id: Circle wallet ID

        Returns:
            BalanceResponse with token balances

        Raises:
            Exception: If balance retrieval fails
        """
        logger.info(f"Getting balance for wallet {wallet_id}")

        try:
            # Get wallet details first
            wallet_response = self.client.wallets.get_wallet(wallet_id)
            wallet = wallet_response.data.wallet

            # Get balance (Circle SDK method)
            # Note: The actual SDK method name may vary
            # This is a placeholder for the balance retrieval logic
            balance_response = self.client.wallets.get_wallet_token_balance(wallet_id)

            balances = []
            if hasattr(balance_response, 'data') and hasattr(balance_response.data, 'token_balances'):
                for token_balance in balance_response.data.token_balances:
                    balances.append({
                        "token": token_balance.token.symbol,
                        "amount": str(token_balance.amount),
                        "decimals": token_balance.token.decimals,
                        "contract_address": token_balance.token.address,
                    })

            return BalanceResponse(
                address=wallet.address,
                blockchain=wallet.blockchain,
                balances=balances,
            )

        except Exception as e:
            logger.error(f"Failed to get balance for wallet {wallet_id}: {e}")
            raise

    async def send_transaction(self, request: SendTransactionRequest) -> TransactionResponse:
        """
        Send a transaction from a wallet

        Args:
            request: Transaction send request

        Returns:
            TransactionResponse with transaction details

        Raises:
            ValueError: If blockchain is not supported
            Exception: If transaction fails
        """
        logger.info(
            f"Sending {request.amount} {request.token_symbol} "
            f"from wallet {request.wallet_id} to {request.to_address}"
        )

        # Validate blockchain
        if not is_supported_network(request.blockchain):
            raise ValueError(f"Unsupported blockchain: {request.blockchain}")

        try:
            # Get wallet details
            wallet_response = self.client.wallets.get_wallet(request.wallet_id)
            wallet = wallet_response.data.wallet

            # Create transaction request
            tx_request = CreateDeveloperTransactionTransferRequest.from_dict({
                "idempotency_key": str(uuid.uuid4()),
                "wallet_id": request.wallet_id,
                "blockchain": request.blockchain,
                "token_id": request.token_symbol,  # e.g., "USDC"
                "destination_address": request.to_address,
                "amounts": [request.amount],
                "fee_level": "MEDIUM",  # LOW, MEDIUM, or HIGH
            })

            # Send transaction
            tx_response = self.client.transactions.create_developer_transaction_transfer(tx_request)
            transaction = tx_response.data

            logger.info(f"✓ Transaction created: {transaction.id}")

            return TransactionResponse(
                transaction_id=transaction.id,
                wallet_id=request.wallet_id,
                status=transaction.state,
                blockchain_tx_hash=None,  # Will be populated when confirmed
                from_address=wallet.address,
                to_address=request.to_address,
                amount=request.amount,
                token_symbol=request.token_symbol,
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise

    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """
        Get transaction status

        Args:
            transaction_id: Circle transaction ID

        Returns:
            Transaction status dictionary or None if not found
        """
        try:
            response = self.client.transactions.get_transaction(transaction_id)
            transaction = response.data.transaction

            return {
                "transaction_id": transaction.id,
                "state": transaction.state,
                "blockchain_tx_hash": getattr(transaction, 'tx_hash', None),
                "created_at": transaction.create_date,
                "updated_at": transaction.update_date,
            }
        except Exception as e:
            logger.error(f"Failed to get transaction status {transaction_id}: {e}")
            return None

    async def list_wallets(self, wallet_set_id: Optional[str] = None) -> List[Dict]:
        """
        List wallets, optionally filtered by wallet set

        Args:
            wallet_set_id: Optional wallet set ID to filter by

        Returns:
            List of wallet dictionaries
        """
        try:
            if wallet_set_id:
                response = self.client.wallets.list_wallets(wallet_set_id=wallet_set_id)
            else:
                response = self.client.wallets.list_wallets()

            wallets = []
            for wallet in response.data.wallets:
                wallets.append({
                    "wallet_id": wallet.id,
                    "wallet_set_id": wallet.wallet_set_id,
                    "address": wallet.address,
                    "blockchain": wallet.blockchain,
                    "account_type": wallet.account_type,
                    "state": wallet.state,
                })

            return wallets

        except Exception as e:
            logger.error(f"Failed to list wallets: {e}")
            raise

    async def list_wallet_sets(self) -> List[Dict]:
        """
        List all wallet sets

        Returns:
            List of wallet set dictionaries
        """
        try:
            response = self.client.wallet_sets.list_wallet_sets()

            wallet_sets = []
            for ws in response.data.wallet_sets:
                wallet_sets.append({
                    "wallet_set_id": ws.id,
                    "name": ws.name,
                    "created_at": ws.create_date,
                })

            return wallet_sets

        except Exception as e:
            logger.error(f"Failed to list wallet sets: {e}")
            raise


# Global service instance
_wallet_service: Optional[WalletService] = None


def get_wallet_service() -> WalletService:
    """Get or initialize the global wallet service"""
    global _wallet_service
    if _wallet_service is None:
        _wallet_service = WalletService()
    return _wallet_service
