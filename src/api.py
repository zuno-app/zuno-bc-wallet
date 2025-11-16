"""
FastAPI REST API for wallet service
Exposes wallet operations to the Rust backend
"""

import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional

from .config import get_config, Config
from .circle_client import init_circle_client, get_circle_client
from .wallet_service import get_wallet_service, WalletService
from .networks import list_networks, get_network
from .models import (
    CreateWalletRequest,
    WalletResponse,
    BalanceResponse,
    SendTransactionRequest,
    TransactionResponse,
    TransactionStatusRequest,
    ListNetworksResponse,
    NetworkInfo,
    HealthCheckResponse,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Zuno Wallet Service",
    description="Embedded wallet service using Circle Developer-Controlled Wallets SDK",
    version="0.1.0",
)


# Dependency: Verify API key
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key from request header"""
    config = get_config()

    # In development, allow missing API key
    if config.service.environment == "development" and not x_api_key:
        return True

    if not x_api_key or x_api_key != config.backend.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return True


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Zuno Wallet Service...")

    try:
        # Load configuration
        config = get_config()
        logger.info(f"✓ Configuration loaded (env: {config.service.environment})")

        # Initialize Circle SDK client
        init_circle_client(config.circle)
        logger.info("✓ Circle SDK client initialized")

        logger.info("✅ Zuno Wallet Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        client = get_circle_client()
        circle_status = "connected" if await client.health_check() else "disconnected"
    except Exception:
        circle_status = "error"

    return HealthCheckResponse(
        status="healthy" if circle_status == "connected" else "degraded",
        circle_api=circle_status,
        timestamp=datetime.utcnow(),
    )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "Zuno Wallet Service",
        "version": "0.1.0",
        "status": "running",
    }


# ============================================================================
# Wallet Endpoints
# ============================================================================

@app.post("/wallets", response_model=WalletResponse, tags=["Wallets"])
async def create_wallet(
    request: CreateWalletRequest,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """Create a new wallet"""
    try:
        return await service.create_wallet(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wallet",
        )


@app.get("/wallets/{wallet_id}", tags=["Wallets"])
async def get_wallet(
    wallet_id: str,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """Get wallet details"""
    wallet = await service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found",
        )
    return wallet


@app.get("/wallets/{wallet_id}/balance", response_model=BalanceResponse, tags=["Wallets"])
async def get_wallet_balance(
    wallet_id: str,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """Get wallet balance"""
    try:
        return await service.get_balance(wallet_id)
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get wallet balance",
        )


@app.get("/wallets", tags=["Wallets"])
async def list_wallets(
    wallet_set_id: Optional[str] = None,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """List wallets"""
    try:
        wallets = await service.list_wallets(wallet_set_id)
        return {"wallets": wallets}
    except Exception as e:
        logger.error(f"Error listing wallets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list wallets",
        )


@app.get("/wallet-sets", tags=["Wallets"])
async def list_wallet_sets(
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """List wallet sets"""
    try:
        wallet_sets = await service.list_wallet_sets()
        return {"wallet_sets": wallet_sets}
    except Exception as e:
        logger.error(f"Error listing wallet sets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list wallet sets",
        )


# ============================================================================
# Transaction Endpoints
# ============================================================================

@app.post("/transactions/send", response_model=TransactionResponse, tags=["Transactions"])
async def send_transaction(
    request: SendTransactionRequest,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """Send a transaction"""
    try:
        return await service.send_transaction(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send transaction",
        )


@app.get("/transactions/{transaction_id}", tags=["Transactions"])
async def get_transaction_status(
    transaction_id: str,
    service: WalletService = Depends(get_wallet_service),
    _: bool = Depends(verify_api_key),
):
    """Get transaction status"""
    transaction = await service.get_transaction_status(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found",
        )
    return transaction


# ============================================================================
# Network Endpoints
# ============================================================================

@app.get("/networks", response_model=ListNetworksResponse, tags=["Networks"])
async def list_supported_networks(_: bool = Depends(verify_api_key)):
    """List all supported blockchain networks"""
    networks = []
    config = get_config()

    for chain_id, network_config in list_networks().items():
        networks.append(
            NetworkInfo(
                chain_id=network_config.chain_id,
                name=network_config.name,
                is_testnet=network_config.is_testnet,
                native_currency=network_config.native_currency,
                supported=chain_id in config.blockchain.supported_blockchains,
            )
        )

    return ListNetworksResponse(networks=networks)


@app.get("/networks/{chain_id}", response_model=NetworkInfo, tags=["Networks"])
async def get_network_info(
    chain_id: str,
    _: bool = Depends(verify_api_key),
):
    """Get information about a specific network"""
    try:
        network_config = get_network(chain_id)
        config = get_config()

        return NetworkInfo(
            chain_id=network_config.chain_id,
            name=network_config.name,
            is_testnet=network_config.is_testnet,
            native_currency=network_config.native_currency,
            supported=chain_id in config.blockchain.supported_blockchains,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {chain_id} not found",
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
            message=str(exc.detail),
        ).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            message="An internal error occurred",
        ).dict(),
    )
