import pytest
from src.models.market_impact import AlmgrenChrissModel

def test_market_impact_calculation():
    model = AlmgrenChrissModel(volatility=0.02)
    temp_impact, perm_impact = model.calculate_market_impact(
        quantity=1.0,
        price=50000.0,
        time_horizon=1.0
    )
    
    assert isinstance(temp_impact, float)
    assert isinstance(perm_impact, float)
    assert temp_impact >= 0
    assert perm_impact >= 0

def test_optimal_execution():
    model = AlmgrenChrissModel(volatility=0.02)
    schedule = model.calculate_optimal_execution(
        quantity=1.0,
        price=50000.0,
        time_horizon=1.0
    )
    
    assert isinstance(schedule, list)
    assert len(schedule) > 0
    assert all(isinstance(x, float) for x in schedule) 