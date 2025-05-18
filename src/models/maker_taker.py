import numpy as np
from typing import List, Tuple
from sklearn.linear_model import LogisticRegression
from dataclasses import dataclass

@dataclass
class OrderbookFeatures:
    spread: float
    depth: float
    imbalance: float
    volatility: float
    volume: float

class MakerTakerPredictor:
    def __init__(self, window_size: int = 1000):
        """
        Initialize the maker/taker predictor
        
        Args:
            window_size: Number of historical data points to consider
        """
        self.window_size = window_size
        self.historical_data = []
        self.model = LogisticRegression(random_state=42)
        self.is_trained = False
        
    def update(self, 
              asks: List[Tuple[float, float]], 
              bids: List[Tuple[float, float]], 
              timestamp: str,
              is_maker: bool):
        """
        Update the model with new orderbook data
        
        Args:
            asks: List of (price, quantity) tuples for ask orders
            bids: List of (price, quantity) tuples for bid orders
            timestamp: Order timestamp
            is_maker: Whether the order was a maker order
        """
        if not asks or not bids:
            return
            
        # Extract features
        features = self._extract_features(asks, bids)
        
        # Store data point
        self.historical_data.append((features, is_maker))
        
        # Keep only recent data
        if len(self.historical_data) > self.window_size:
            self.historical_data.pop(0)
            
        # Update model if we have enough data
        if len(self.historical_data) >= 100 and not self.is_trained:
            self._train_model()
            
    def predict_proportion(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]]) -> float:
        """
        Predict the probability of an order being a maker order
        
        Args:
            asks: List of (price, quantity) tuples for ask orders
            bids: List of (price, quantity) tuples for bid orders
            
        Returns:
            Probability of being a maker order (0-1)
        """
        if not asks or not bids:
            return 0.5  # Default to 50/50 if no data
            
        features = self._extract_features(asks, bids)
        
        if not self.is_trained:
            return self._simple_proportion_model(asks, bids)
            
        # Predict using the trained model
        return self.model.predict_proba([features])[0][1]
        
    def _extract_features(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]]) -> OrderbookFeatures:
        """Extract features from orderbook data"""
        if not asks or not bids:
            return OrderbookFeatures(0, 0, 0, 0, 0)
            
        # Calculate spread
        best_ask = float(asks[0][0])
        best_bid = float(bids[0][0])
        spread = best_ask - best_bid
        
        # Calculate depth (total volume in top 5 levels)
        ask_depth = sum(float(q) for _, q in asks[:5])
        bid_depth = sum(float(q) for _, q in bids[:5])
        total_depth = ask_depth + bid_depth
        
        # Calculate imbalance
        imbalance = (bid_depth - ask_depth) / total_depth if total_depth > 0 else 0
        
        # Calculate volatility (price changes across levels)
        ask_prices = [float(p) for p, _ in asks[:5]]
        bid_prices = [float(p) for p, _ in bids[:5]]
        volatility = np.std(ask_prices + bid_prices) if len(ask_prices + bid_prices) > 1 else 0
        
        # Calculate total volume
        total_volume = sum(float(q) for _, q in asks[:10] + bids[:10])
        
        return OrderbookFeatures(
            spread=spread,
            depth=total_depth,
            imbalance=imbalance,
            volatility=volatility,
            volume=total_volume
        )
        
    def _train_model(self):
        """Train the logistic regression model"""
        if len(self.historical_data) < 100:
            return
            
        X = np.array([[
            d.spread,
            d.depth,
            d.imbalance,
            d.volatility,
            d.volume
        ] for d, _ in self.historical_data])
        
        y = np.array([is_maker for _, is_maker in self.historical_data])
        
        self.model.fit(X, y)
        self.is_trained = True
        
    def _simple_proportion_model(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]]) -> float:
        """Simple model for when we don't have enough training data"""
        if not asks or not bids:
            return 0.5
            
        # Calculate basic features
        spread = float(asks[0][0]) - float(bids[0][0])
        mid_price = (float(asks[0][0]) + float(bids[0][0])) / 2
        normalized_spread = spread / mid_price
        
        # Simple heuristic: higher spread favors maker orders
        maker_prob = min(0.8, max(0.2, 0.5 + normalized_spread * 10))
        return maker_prob 