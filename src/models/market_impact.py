import numpy as np
from typing import Tuple


class AlmgrenChrissModel:
    def __init__(self, volatility: float, eta: float = 0.1, gamma: float = 0.1):
        """
        Initialize the Almgren-Chriss model
        
        Args:
            volatility: Market volatility
            eta: Temporary market impact parameter
            gamma: Permanent market impact parameter
        """
        self.volatility = volatility
        self.eta = eta
        self.gamma = gamma

    def calculate_market_impact(self, quantity: float, price: float, time_horizon: float) -> Tuple[float, float]:
        """
        Calculate temporary and permanent market impact
        
        Args:
            quantity: Order quantity
            price: Current market price
            time_horizon: Trading horizon in days
            
        Returns:
            Tuple of (temporary_impact, permanent_impact)
        """
        # Temporary impact
        temp_impact = self.eta * (quantity / price) * np.sqrt(quantity / time_horizon)
        
        # Permanent impact
        perm_impact = self.gamma * (quantity / price)
        
        return temp_impact, perm_impact

    def calculate_optimal_execution(self, quantity: float, price: float, time_horizon: float) -> np.ndarray:
        """
        Calculate optimal execution schedule
        
        Args:
            quantity: Total order quantity
            price: Current market price
            time_horizon: Trading horizon in days
            
        Returns:
            Array of optimal execution quantities
        """
        n_steps = 10  # Number of execution steps
        t = np.linspace(0, time_horizon, n_steps)
        
        # Calculate optimal trading rate
        k = np.sqrt(self.eta * self.volatility / self.gamma)
        optimal_rate = quantity * np.cosh(k * (time_horizon - t)) / np.cosh(k * time_horizon)
        
        return optimal_rate 