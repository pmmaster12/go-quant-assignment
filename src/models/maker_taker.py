import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import List, Tuple

class MakerTakerModel:
    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False

    def prepare_features(self, orderbook_data: dict) -> np.ndarray:
        """Extract features for maker/taker prediction"""
        asks = orderbook_data.get('asks', [])
        bids = orderbook_data.get('bids', [])
        
        # Calculate features
        spread = float(asks[0][0]) - float(bids[0][0]) if asks and bids else 0
        ask_depth = sum(float(qty) for _, qty in asks[:5])
        bid_depth = sum(float(qty) for _, qty in bids[:5])
        depth_ratio = ask_depth / bid_depth if bid_depth > 0 else 1.0
        
        return np.array([[spread, depth_ratio]])

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the maker/taker prediction model"""
        self.model.fit(X, y)
        self.is_trained = True 