"""
Zuno Embedded Wallet Service
Entry point for the FastAPI application
"""

import logging
import uvicorn
from src.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    try:
        # Load configuration
        config = get_config()

        logger.info("=" * 70)
        logger.info("Zuno Embedded Wallet Service")
        logger.info("=" * 70)
        logger.info(f"Environment: {config.service.environment}")
        logger.info(f"Host: {config.service.host}")
        logger.info(f"Port: {config.service.port}")
        logger.info(f"Default Blockchain: {config.blockchain.default_blockchain}")
        logger.info(f"Supported Blockchains: {', '.join(config.blockchain.supported_blockchains)}")
        logger.info("=" * 70)

        # Run FastAPI application with uvicorn
        uvicorn.run(
            "src.api:app",
            host=config.service.host,
            port=config.service.port,
            reload=config.service.environment == "development",
            log_level=config.service.log_level.lower(),
        )

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise


if __name__ == "__main__":
    main()
