import numpy as np
from typing import List, Tuple
from sklearn.linear_model import QuantileRegressor

class SlippageModel:
    def __init__(self, window_size: int = 100):
        """
        Initialize the slippage model
        
        Args:
            window_size: Number of historical data points to consider
        """
        self.window_size = window_size
        self.historical_data = []
        self.model = QuantileRegressor(quantile=0.5, alpha=0.1, solver='highs')
        
    def update(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]], quantity: float):
        """
        Update the model with new orderbook data
        
        Args:
            asks: List of (price, quantity) tuples for ask orders
            bids: List of (price, quantity) tuples for bid orders
            quantity: Order quantity in base currency
        """
        if not asks or not bids:
            return
            
        mid_price = (float(asks[0][0]) + float(bids[0][0])) / 2
        spread = float(asks[0][0]) - float(bids[0][0])
        
        # Calculate volume-weighted average price (VWAP)
        ask_vwap = self._calculate_vwap(asks)
        bid_vwap = self._calculate_vwap(bids)
        
        # Calculate orderbook imbalance
        total_ask_volume = sum(float(q) for _, q in asks)
        total_bid_volume = sum(float(q) for _, q in bids)
        imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        # Store features for regression
        features = np.array([[
            spread / mid_price,  # Normalized spread
            imbalance,           # Orderbook imbalance
            quantity / total_ask_volume,  # Relative order size
            (ask_vwap - mid_price) / mid_price,  # Ask-side pressure
            (mid_price - bid_vwap) / mid_price   # Bid-side pressure
        ]])
        
        # Calculate actual slippage
        if quantity > 0:  # Buy order
            actual_slippage = (ask_vwap - mid_price) / mid_price
        else:  # Sell order
            actual_slippage = (mid_price - bid_vwap) / mid_price
            
        self.historical_data.append((features, actual_slippage))
        
        # Keep only recent data
        if len(self.historical_data) > self.window_size:
            self.historical_data.pop(0)
            
        # Update model if we have enough data
        if len(self.historical_data) >= 10:
            X = np.vstack([x for x, _ in self.historical_data])
            y = np.array([y for _, y in self.historical_data])
            self.model.fit(X, y)
    
    def predict_slippage(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]], quantity: float) -> float:
        """
        Predict expected slippage for a given order
        
        Args:
            asks: List of (price, quantity) tuples for ask orders
            bids: List of (price, quantity) tuples for bid orders
            quantity: Order quantity in base currency
            
        Returns:
            Predicted slippage as a percentage
        """
        if not asks or not bids:
            return 0.0
            
        mid_price = (float(asks[0][0]) + float(bids[0][0])) / 2
        spread = float(asks[0][0]) - float(bids[0][0])
        
        # Calculate features
        total_ask_volume = sum(float(q) for _, q in asks)
        total_bid_volume = sum(float(q) for _, q in bids)
        imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        ask_vwap = self._calculate_vwap(asks)
        bid_vwap = self._calculate_vwap(bids)
        
        features = np.array([[
            spread / mid_price,
            imbalance,
            quantity / total_ask_volume,
            (ask_vwap - mid_price) / mid_price,
            (mid_price - bid_vwap) / mid_price
        ]])
        
        # If we don't have enough historical data, use a simple model
        if len(self.historical_data) < 10:
            return self._simple_slippage_model(asks, bids, quantity)
            
        # Predict using the trained model
        predicted_slippage = self.model.predict(features)[0]
        return max(0.0, predicted_slippage)  # Ensure non-negative slippage
    
    def _calculate_vwap(self, orders: List[Tuple[float, float]]) -> float:
        """Calculate Volume-Weighted Average Price"""
        total_volume = 0
        weighted_price = 0
        
        for price, quantity in orders:
            price = float(price)
            quantity = float(quantity)
            total_volume += quantity
            weighted_price += price * quantity
            
        return weighted_price / total_volume if total_volume > 0 else 0
    
    def _simple_slippage_model(self, asks: List[Tuple[float, float]], bids: List[Tuple[float, float]], quantity: float) -> float:
        """Simple slippage model for when we don't have enough historical data"""
        if not asks or not bids:
            return 0.0
            
        mid_price = (float(asks[0][0]) + float(bids[0][0])) / 2
        spread = float(asks[0][0]) - float(bids[0][0])
        
        # Calculate basic slippage based on order size relative to available liquidity
        total_ask_volume = sum(float(q) for _, q in asks)
        relative_size = quantity / total_ask_volume
        
        # Simple linear model: slippage increases with relative order size and spread
        return (spread / mid_price) * (1 + relative_size) 