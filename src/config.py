"""
Configuration module for wallet service
Loads configuration from environment variables
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class CircleConfig:
    """Circle API configuration"""

    api_key: str
    entity_secret: str

    @classmethod
    def from_env(cls) -> "CircleConfig":
        """Load Circle configuration from environment variables"""
        api_key = os.environ.get("CIRCLE_API_KEY")
        entity_secret = os.environ.get("CIRCLE_ENTITY_SECRET")

        if not api_key:
            raise ValueError("CIRCLE_API_KEY environment variable not set")

        if not entity_secret:
            raise ValueError("CIRCLE_ENTITY_SECRET environment variable not set")

        return cls(api_key=api_key, entity_secret=entity_secret)


@dataclass
class ServiceConfig:
    """Service configuration"""

    host: str
    port: int
    environment: str
    log_level: str
    log_format: str

    @classmethod
    def from_env(cls) -> "ServiceConfig":
        """Load service configuration from environment variables"""
        return cls(
            host=os.environ.get("SERVICE_HOST", "0.0.0.0"),
            port=int(os.environ.get("SERVICE_PORT", "8000")),
            environment=os.environ.get("SERVICE_ENV", "development"),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            log_format=os.environ.get("LOG_FORMAT", "json"),
        )


@dataclass
class BlockchainConfig:
    """Blockchain network configuration"""

    default_blockchain: str
    supported_blockchains: list[str]

    @classmethod
    def from_env(cls) -> "BlockchainConfig":
        """Load blockchain configuration from environment variables"""
        default_blockchain = os.environ.get("DEFAULT_BLOCKCHAIN", "ARC-TESTNET")

        supported_str = os.environ.get(
            "SUPPORTED_BLOCKCHAINS", "ARC-TESTNET,MATIC-AMOY,ARB-SEPOLIA"
        )
        supported_blockchains = [b.strip() for b in supported_str.split(",")]

        return cls(
            default_blockchain=default_blockchain,
            supported_blockchains=supported_blockchains,
        )


@dataclass
class BackendConfig:
    """Backend API integration configuration"""

    api_url: str
    api_key: str
    timeout_seconds: int

    @classmethod
    def from_env(cls) -> "BackendConfig":
        """Load backend configuration from environment variables"""
        return cls(
            api_url=os.environ.get("BACKEND_API_URL", "http://localhost:8080"),
            api_key=os.environ.get("BACKEND_API_KEY", ""),
            timeout_seconds=int(os.environ.get("WALLET_SERVICE_TIMEOUT_SECONDS", "30")),
        )


@dataclass
class RedisConfig:
    """Redis configuration for caching"""

    url: str
    db: int

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Load Redis configuration from environment variables"""
        return cls(
            url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
            db=int(os.environ.get("REDIS_DB", "1")),
        )


@dataclass
class Config:
    """Complete wallet service configuration"""

    circle: CircleConfig
    service: ServiceConfig
    blockchain: BlockchainConfig
    backend: BackendConfig
    redis: RedisConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Load complete configuration from environment variables"""
        return cls(
            circle=CircleConfig.from_env(),
            service=ServiceConfig.from_env(),
            blockchain=BlockchainConfig.from_env(),
            backend=BackendConfig.from_env(),
            redis=RedisConfig.from_env(),
        )


# Global config instance
config: Config | None = None


def get_config() -> Config:
    """Get or initialize the global configuration"""
    global config
    if config is None:
        config = Config.from_env()
    return config
