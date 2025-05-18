# GoQuant Trade Simulator

A high-performance trade simulator that leverages real-time market data to estimate transaction costs and market impact for cryptocurrency trading.

## Features

- Real-time L2 orderbook data processing
- Sophisticated market impact modeling using Almgren-Chriss
- Slippage prediction using quantile regression
- Fee calculation based on OKX fee tiers
- Maker/Taker proportion prediction
- Latency measurement and monitoring
- Modern PyQt5-based user interface

## Architecture

The simulator is built with a modular architecture consisting of several key components:

### Core Components

1. **WebSocket Client**
   - Connects to OKX's WebSocket API
   - Processes real-time L2 orderbook data
   - Implements automatic reconnection
   - Measures network latency

2. **Market Impact Model**
   - Implements Almgren-Chriss model
   - Calculates temporary and permanent market impact
   - Optimizes execution schedule
   - Considers volatility and order size

3. **Slippage Model**
   - Uses quantile regression for prediction
   - Considers orderbook depth and imbalance
   - Adapts to market conditions
   - Provides confidence intervals

4. **Fee Calculator**
   - Implements OKX's fee tier structure
   - Calculates maker/taker fees
   - Supports volume-based tier selection
   - Handles different order types

5. **Maker/Taker Predictor**
   - Uses logistic regression
   - Considers orderbook features
   - Adapts to market conditions
   - Provides probability estimates

### User Interface

The UI is built with PyQt5 and features:

- Left panel: Input parameters
  - Exchange selection
  - Asset selection
  - Order quantity
  - Volatility setting
  - Fee tier selection

- Right panel: Output metrics
  - Expected slippage
  - Expected fees
  - Market impact
  - Net cost
  - Maker/Taker ratio
  - Processing latency

## Performance Optimizations

1. **Data Processing**
   - Efficient orderbook data structures
   - Batch processing of updates
   - Memory-efficient feature calculation
   - Optimized numerical computations

2. **UI Updates**
   - Asynchronous data processing
   - Efficient UI update scheduling
   - Minimal UI thread blocking
   - Smooth real-time updates

3. **Model Efficiency**
   - Incremental model updates
   - Efficient feature extraction
   - Optimized regression calculations
   - Memory-efficient data storage

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/goquant-simulator.git
   cd goquant-simulator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the simulator:
   ```bash
   python src/main.py
   ```

2. Configure input parameters:
   - Select exchange (OKX)
   - Choose trading pair
   - Set order quantity
   - Adjust volatility
   - Select fee tier

3. Monitor output metrics:
   - Real-time slippage estimates
   - Fee calculations
   - Market impact analysis
   - Maker/Taker predictions
   - Processing latency

## Model Details

### Almgren-Chriss Model

The market impact model implements the Almgren-Chriss framework with:

- Temporary impact: η * (Q/V) * √(Q/T)
- Permanent impact: γ * (Q/V)
- Optimal execution: √(ησ/γ)

Where:
- η: Temporary impact parameter
- γ: Permanent impact parameter
- Q: Order quantity
- V: Market volume
- T: Time horizon
- σ: Volatility

### Slippage Model

The slippage prediction uses quantile regression with features:

- Normalized spread
- Orderbook imbalance
- Relative order size
- Price pressure indicators
- Volume profile

### Maker/Taker Model

The maker/taker prediction uses logistic regression with features:

- Spread
- Orderbook depth
- Volume imbalance
- Price volatility
- Total volume

## Performance Metrics

The simulator tracks several performance metrics:

1. **Processing Latency**
   - Data processing time
   - Model update time
   - UI update time
   - End-to-end latency

2. **Model Accuracy**
   - Slippage prediction error
   - Market impact estimation
   - Maker/Taker prediction accuracy
   - Fee calculation precision

3. **System Performance**
   - Memory usage
   - CPU utilization
   - Network bandwidth
   - UI responsiveness

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OKX for providing market data
- Almgren and Chriss for their market impact model
- PyQt5 team for the UI framework
- Python community for excellent libraries 