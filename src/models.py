"""
Pydantic models for wallet API requests and responses
"""

from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Wallet Models
# ============================================================================

class CreateWalletRequest(BaseModel):
    """Request to create a new wallet"""

    user_id: str = Field(..., description="User ID from the backend")
    blockchain: str = Field(..., description="Blockchain network (e.g., ARC-TESTNET)")
    account_type: str = Field(default="SCA", description="Account type: SCA or EOA")
    wallet_set_name: Optional[str] = Field(None, description="Optional wallet set name")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "blockchain": "ARC-TESTNET",
                "account_type": "SCA",
                "wallet_set_name": "user_main_wallet_set",
            }
        }


class WalletResponse(BaseModel):
    """Response with wallet information"""

    wallet_id: str = Field(..., description="Circle wallet ID")
    wallet_set_id: str = Field(..., description="Circle wallet set ID")
    address: str = Field(..., description="Blockchain address")
    blockchain: str = Field(..., description="Blockchain network")
    account_type: str = Field(..., description="Account type")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "wallet_id": "01234567-89ab-cdef-0123-456789abcdef",
                "wallet_set_id": "01234567-89ab-cdef-0123-456789abcdef",
                "address": "0x1234567890abcdef1234567890abcdef12345678",
                "blockchain": "ARC-TESTNET",
                "account_type": "SCA",
                "created_at": "2025-11-16T12:00:00Z",
            }
        }


class BalanceResponse(BaseModel):
    """Response with wallet balance"""

    address: str = Field(..., description="Wallet address")
    blockchain: str = Field(..., description="Blockchain network")
    balances: list[dict] = Field(..., description="List of token balances")

    class Config:
        json_schema_extra = {
            "example": {
                "address": "0x1234567890abcdef1234567890abcdef12345678",
                "blockchain": "ARC-TESTNET",
                "balances": [
                    {
                        "token": "USDC",
                        "amount": "100.50",
                        "decimals": 6,
                        "contract_address": "0xtoken_address",
                    }
                ],
            }
        }


# ============================================================================
# Transaction Models
# ============================================================================

class SendTransactionRequest(BaseModel):
    """Request to send a transaction"""

    wallet_id: str = Field(..., description="Circle wallet ID")
    to_address: str = Field(..., description="Recipient address")
    token_symbol: str = Field(..., description="Token to send (e.g., USDC)")
    amount: str = Field(..., description="Amount to send (as string to avoid precision loss)")
    blockchain: str = Field(..., description="Blockchain network")

    class Config:
        json_schema_extra = {
            "example": {
                "wallet_id": "01234567-89ab-cdef-0123-456789abcdef",
                "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "token_symbol": "USDC",
                "amount": "10.50",
                "blockchain": "ARC-TESTNET",
            }
        }


class TransactionResponse(BaseModel):
    """Response with transaction information"""

    transaction_id: str = Field(..., description="Circle transaction ID")
    wallet_id: str = Field(..., description="Wallet ID")
    status: str = Field(..., description="Transaction status")
    blockchain_tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: str = Field(..., description="Transaction amount")
    token_symbol: str = Field(..., description="Token symbol")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "01234567-89ab-cdef-0123-456789abcdef",
                "wallet_id": "01234567-89ab-cdef-0123-456789abcdef",
                "status": "PENDING",
                "blockchain_tx_hash": None,
                "from_address": "0x1234567890abcdef1234567890abcdef12345678",
                "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "amount": "10.50",
                "token_symbol": "USDC",
                "created_at": "2025-11-16T12:00:00Z",
            }
        }


class TransactionStatusRequest(BaseModel):
    """Request to get transaction status"""

    transaction_id: str = Field(..., description="Circle transaction ID")


# ============================================================================
# Network Models
# ============================================================================

class NetworkInfo(BaseModel):
    """Information about a blockchain network"""

    chain_id: str = Field(..., description="Circle chain ID (e.g., ARC-TESTNET)")
    name: str = Field(..., description="Human-readable name")
    is_testnet: bool = Field(..., description="Whether this is a testnet")
    native_currency: str = Field(..., description="Native currency symbol")
    supported: bool = Field(..., description="Whether this network is currently supported")

    class Config:
        json_schema_extra = {
            "example": {
                "chain_id": "ARC-TESTNET",
                "name": "Arc Testnet",
                "is_testnet": True,
                "native_currency": "ARC",
                "supported": True,
            }
        }


class ListNetworksResponse(BaseModel):
    """Response with list of supported networks"""

    networks: list[NetworkInfo] = Field(..., description="List of network configurations")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "WALLET_NOT_FOUND",
                "message": "Wallet with ID 123 not found",
                "details": {"wallet_id": "123"},
            }
        }


# ============================================================================
# Health Check
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    circle_api: str = Field(..., description="Circle API connectivity status")
    timestamp: datetime = Field(..., description="Current timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "circle_api": "connected",
                "timestamp": "2025-11-16T12:00:00Z",
            }
        }
