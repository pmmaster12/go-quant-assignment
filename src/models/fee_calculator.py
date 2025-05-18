from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class FeeTier:
    maker_fee: float
    taker_fee: float
    min_volume: float  # 30-day trading volume in USD

class FeeCalculator:
    def __init__(self):
        # OKX fee tiers as of 2024
        self.fee_tiers = [
            FeeTier(0.08, 0.10, 0),           # Tier 1
            FeeTier(0.07, 0.09, 50000),       # Tier 2
            FeeTier(0.06, 0.08, 100000),      # Tier 3
            FeeTier(0.05, 0.07, 200000),      # Tier 4
            FeeTier(0.04, 0.06, 500000),      # Tier 5
            FeeTier(0.03, 0.05, 1000000),     # Tier 6
            FeeTier(0.02, 0.04, 2000000),     # Tier 7
            FeeTier(0.01, 0.03, 5000000),     # Tier 8
            FeeTier(0.00, 0.02, 10000000),    # Tier 9
        ]
        
    def calculate_fees(self, 
                      order_type: str,
                      quantity: float,
                      price: float,
                      fee_tier: int,
                      is_maker: bool = False) -> Tuple[float, float]:
        """
        Calculate trading fees for an order
        
        Args:
            order_type: Type of order ('market' or 'limit')
            quantity: Order quantity in base currency
            price: Order price in quote currency
            fee_tier: Fee tier (1-9)
            is_maker: Whether the order is a maker order
            
        Returns:
            Tuple of (fee_amount, fee_percentage)
        """
        if not 1 <= fee_tier <= 9:
            raise ValueError("Fee tier must be between 1 and 9")
            
        # Get fee rates for the specified tier
        tier = self.fee_tiers[fee_tier - 1]
        
        # Determine fee rate based on order type and maker/taker status
        if order_type == 'market':
            fee_rate = tier.taker_fee
        else:  # limit order
            fee_rate = tier.maker_fee if is_maker else tier.taker_fee
            
        # Calculate fee amount
        order_value = quantity * price
        fee_amount = order_value * (fee_rate / 100)
        
        return fee_amount, fee_rate
        
    def get_tier_for_volume(self, volume_30d: float) -> int:
        """
        Determine the appropriate fee tier based on 30-day trading volume
        
        Args:
            volume_30d: 30-day trading volume in USD
            
        Returns:
            Fee tier (1-9)
        """
        for i, tier in enumerate(self.fee_tiers, 1):
            if volume_30d >= tier.min_volume:
                return i
        return 1  # Default to tier 1 if volume is below all thresholds 