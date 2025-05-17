# Trade Simulator

A high-performance trade simulator leveraging real-time market data to estimate transaction costs and market impact. This system connects to WebSocket endpoints that stream full L2 orderbook data for cryptocurrency exchanges.

## Features

- Real-time L2 orderbook data processing
- Market impact estimation using Almgren-Chriss model
- Slippage calculation using regression modeling
- Fee calculation based on exchange tiers
- Maker/Taker proportion prediction
- Performance monitoring and optimization

## Prerequisites

- Python 3.8 or higher
- VPN connection (required for OKX access)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trade-simulator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Activate VPN** (required for OKX access).

3. **Run the application:**
    ```bash
    python src/main.py
    ```

4. **Logs** will be generated in `trade_simulator.log`.

## Input Parameters

- **Exchange:** OKX (default)
- **Asset:** BTC-USDT-SWAP (default)
- **Order Type:** Market (default)
- **Quantity:** User input (USD equivalent)
- **Volatility:** User input
- **Fee Tier:** User selection

## Output Parameters

- **Expected Slippage:** Estimated using regression modeling
- **Expected Fees:** Calculated based on fee tier
- **Market Impact:** Estimated using the Almgren-Chriss model
- **Net Cost:** Sum of slippage, fees, and market impact
- **Maker/Taker Proportion:** Predicted using logistic regression
- **Internal Latency:** Processing time per tick

## Models and Algorithms

### **Almgren-Chriss Market Impact Model**
- Used to estimate the cost of executing large orders in a market.
- Considers both temporary and permanent market impact.
- See: [Understanding Almgren-Chriss Model](https://www.linkedin.com/pulse/understanding-almgren-chriss-model-optimal-portfolio-execution-pal-pmeqc/)

### **Slippage Estimation**
- Uses linear or quantile regression to estimate the difference between expected and actual execution price.

### **Maker/Taker Proportion**
- Uses logistic regression to predict the likelihood of an order being a maker or taker.

### **Fee Calculation**
- Rule-based, according to OKX fee tiers.

## Performance Monitoring

- **Data processing latency**
- **UI update latency**
- **End-to-end simulation loop latency**
- All metrics are logged and can be reviewed in `trade_simulator.log`.

## Logging

- All major events, errors, and performance metrics are logged to `trade_simulator.log` and the console.
- Logging is set up in `src/logger.py`.

## Development & Testing

- **Unit tests** are in the `tests/` directory.
- Run tests with:
    ```bash
    python -m pytest tests/
    ```

## Troubleshooting

- If output parameters do not update, check:
    - VPN connection
    - WebSocket endpoint accessibility
    - Log file for errors

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

For questions or support, please open an issue or contact the maintainer.

## Project Structure

```
trade_simulator/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── market_impact.py
│   │   ├── slippage.py
│   │   └── maker_taker.py
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── orderbook_client.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── utils/
│       ├── __init__.py
│       └── performance.py
└── tests/
    └── __init__.py
```

## Components

### Market Impact Model
The Almgren-Chriss model is implemented to estimate market impact, considering:
- Temporary market impact
- Permanent market impact
- Optimal execution scheduling

### Slippage Estimation
Uses regression modeling to predict slippage based on:
- Order size
- Market depth
- Volatility

### Fee Calculation
Implements rule-based fee models based on:
- Exchange fee tiers
- Trading volume
- Asset type

### Performance Monitoring
Tracks:
- Data processing latency
- UI update latency
- End-to-end simulation loop latency

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines. To check your code:
```bash
flake8 src/
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 