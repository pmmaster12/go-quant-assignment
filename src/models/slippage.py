import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple

class SlippageModel:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False

    def prepare_features(self, orderbook_data: dict) -> np.ndarray:
        """Extract features from orderbook data for slippage prediction"""
        asks = orderbook_data.get('asks', [])
        bids = orderbook_data.get('bids', [])
        
        # Calculate features
        spread = float(asks[0][0]) - float(bids[0][0]) if asks and bids else 0
        depth = sum(float(price) * float(qty) for price, qty in asks[:5])
        volatility = self._calculate_volatility(asks, bids)
        
        return np.array([[spread, depth, volatility]])

    def _calculate_volatility(self, asks: List[Tuple[str, str]], bids: List[Tuple[str, str]]) -> float:
        """Calculate price volatility from orderbook data"""
        if not asks or not bids:
            return 0.0
            
        mid_prices = []
        for i in range(min(len(asks), len(bids))):
            mid_price = (float(asks[i][0]) + float(bids[i][0])) / 2
            mid_prices.append(mid_price)
            
        return np.std(mid_prices) if mid_prices else 0.0

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the slippage prediction model"""
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, orderbook_data: dict) -> float:
        """Predict slippage for given orderbook data"""
        if not self.is_trained:
            return 0.0
            
        features = self.prepare_features(orderbook_data)
        return self.model.predict(features)[0] 