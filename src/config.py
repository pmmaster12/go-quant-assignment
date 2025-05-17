import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WebSocket Configuration
WEBSOCKET_URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

# UI Configuration
UI_UPDATE_INTERVAL_MS = 100
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Model Parameters
DEFAULT_VOLATILITY = 0.02
DEFAULT_ETA = 0.1  # Temporary market impact parameter
DEFAULT_GAMMA = 0.1  # Permanent market impact parameter

# Fee Tiers
FEE_TIERS = {
    "Tier 1": 0.08,  # 0.08%
    "Tier 2": 0.07,  # 0.07%
    "Tier 3": 0.06,  # 0.06%
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 