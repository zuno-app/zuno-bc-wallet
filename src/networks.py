"""
Blockchain network configurations
Supports multiple networks including Arc, Polygon, Arbitrum, etc.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class NetworkConfig:
    """Configuration for a blockchain network"""

    chain_id: str  # Circle's chain identifier
    name: str
    is_testnet: bool
    native_currency: str
    explorer_url: str


# Network configurations
NETWORKS: Dict[str, NetworkConfig] = {
    # Arc Networks
    "ARC-TESTNET": NetworkConfig(
        chain_id="ARC-TESTNET",
        name="Arc Testnet",
        is_testnet=True,
        native_currency="ARC",
        explorer_url="https://testnet.arcscan.com",
    ),
    "ARC-MAINNET": NetworkConfig(
        chain_id="ARC-MAINNET",
        name="Arc Mainnet",
        is_testnet=False,
        native_currency="ARC",
        explorer_url="https://arcscan.com",
    ),
    # Polygon Networks
    "MATIC-AMOY": NetworkConfig(
        chain_id="MATIC-AMOY",
        name="Polygon Amoy Testnet",
        is_testnet=True,
        native_currency="MATIC",
        explorer_url="https://amoy.polygonscan.com",
    ),
    "MATIC-MAINNET": NetworkConfig(
        chain_id="MATIC-MAINNET",
        name="Polygon Mainnet",
        is_testnet=False,
        native_currency="MATIC",
        explorer_url="https://polygonscan.com",
    ),
    # Arbitrum Networks
    "ARB-SEPOLIA": NetworkConfig(
        chain_id="ARB-SEPOLIA",
        name="Arbitrum Sepolia Testnet",
        is_testnet=True,
        native_currency="ETH",
        explorer_url="https://sepolia.arbiscan.io",
    ),
    "ARB-MAINNET": NetworkConfig(
        chain_id="ARB-MAINNET",
        name="Arbitrum One Mainnet",
        is_testnet=False,
        native_currency="ETH",
        explorer_url="https://arbiscan.io",
    ),
    # Ethereum Networks
    "ETH-SEPOLIA": NetworkConfig(
        chain_id="ETH-SEPOLIA",
        name="Ethereum Sepolia Testnet",
        is_testnet=True,
        native_currency="ETH",
        explorer_url="https://sepolia.etherscan.io",
    ),
    "ETH-MAINNET": NetworkConfig(
        chain_id="ETH-MAINNET",
        name="Ethereum Mainnet",
        is_testnet=False,
        native_currency="ETH",
        explorer_url="https://etherscan.io",
    ),
    # Avalanche Networks
    "AVAX-FUJI": NetworkConfig(
        chain_id="AVAX-FUJI",
        name="Avalanche Fuji Testnet",
        is_testnet=True,
        native_currency="AVAX",
        explorer_url="https://testnet.snowtrace.io",
    ),
    "AVAX-MAINNET": NetworkConfig(
        chain_id="AVAX-MAINNET",
        name="Avalanche C-Chain Mainnet",
        is_testnet=False,
        native_currency="AVAX",
        explorer_url="https://snowtrace.io",
    ),
    # Solana Networks (if supported by Circle)
    "SOL-DEVNET": NetworkConfig(
        chain_id="SOL-DEVNET",
        name="Solana Devnet",
        is_testnet=True,
        native_currency="SOL",
        explorer_url="https://explorer.solana.com/?cluster=devnet",
    ),
    "SOL-MAINNET": NetworkConfig(
        chain_id="SOL-MAINNET",
        name="Solana Mainnet",
        is_testnet=False,
        native_currency="SOL",
        explorer_url="https://explorer.solana.com",
    ),
}


def get_network(chain_id: str) -> NetworkConfig:
    """Get network configuration by chain ID"""
    if chain_id not in NETWORKS:
        raise ValueError(f"Unsupported network: {chain_id}")
    return NETWORKS[chain_id]


def is_supported_network(chain_id: str) -> bool:
    """Check if a network is supported"""
    return chain_id in NETWORKS


def list_networks(testnet_only: bool = False, mainnet_only: bool = False) -> Dict[str, NetworkConfig]:
    """List all configured networks"""
    if testnet_only:
        return {k: v for k, v in NETWORKS.items() if v.is_testnet}
    elif mainnet_only:
        return {k: v for k, v in NETWORKS.items() if not v.is_testnet}
    return NETWORKS


def get_explorer_url(chain_id: str, tx_hash: str) -> str:
    """Get blockchain explorer URL for a transaction"""
    network = get_network(chain_id)
    return f"{network.explorer_url}/tx/{tx_hash}"


def get_address_explorer_url(chain_id: str, address: str) -> str:
    """Get blockchain explorer URL for an address"""
    network = get_network(chain_id)
    return f"{network.explorer_url}/address/{address}"
