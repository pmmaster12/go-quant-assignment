# High-Performance Trade Simulator

A real-time trade simulator that processes market data and calculates various trading metrics using sophisticated models.

## Architecture

### System Overview
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  WebSocket      │     │  Data           │     │  UI             │
│  Client         │────▶│  Processor      │────▶│  Components     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                        │
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Market         │     │  Trading        │     │  Performance    │
│  Models         │     │  Metrics        │     │  Monitor        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  WebSocket  │    │  Data       │    │  Trading    │    │  UI         │
│  Message    │───▶│  Queue      │───▶│  Models     │───▶│  Update     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                 │                   │                  │
       │                 │                   │                  │
       ▼                 ▼                   ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Validation │    │  Processing │    │  Metrics    │    │  Display    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Components

1. **WebSocket Client**
   ```python
   class OrderbookClient:
       def __init__(self, url: str, callback: Callable):
           self.url = url
           self.callback = callback
           self.running = True
           self.reconnect_delay = 1.0
           self.max_reconnect_delay = 30.0
           self.last_message_time = 0
           self.heartbeat_interval = 30

       async def connect(self):
           while self.running:
               try:
                   async with websockets.connect(
                       self.url,
                       ping_interval=20,
                       ping_timeout=10,
                       close_timeout=5
                   ) as ws:
                       self.ws = ws
                       while self.running:
                           message = await ws.recv()
                           self.callback(json.loads(message))
               except Exception as e:
                   await asyncio.sleep(self.reconnect_delay)
                   self.reconnect_delay = min(
                       self.reconnect_delay * 2,
                       self.max_reconnect_delay
                   )
   ```

2. **Data Processor**
   ```python
   def process_orderbook_data(self, data: dict):
       # Validate and normalize orderbook data
       asks = [(float(price), float(qty)) 
              for price, qty in data.get('asks', [])
              if float(price) > 0 and float(qty) > 0]
       bids = [(float(price), float(qty))
              for price, qty in data.get('bids', [])
              if float(price) > 0 and float(qty) > 0]
       
       # Sort and validate
       asks.sort(key=lambda x: x[0])
       bids.sort(key=lambda x: x[0], reverse=True)
       
       # Detect and handle outliers
       self._handle_price_gaps(asks, bids)
       
       return asks, bids
   ```

3. **Trading Models**

   a. **Slippage Model**
   ```python
   class SlippageModel:
       def __init__(self):
           self.model = QuantileRegressor(
               quantiles=[0.1, 0.5, 0.9],
               solver='highs'
           )
           
       def predict_slippage(self, asks, bids, quantity):
           features = self._extract_features(asks, bids, quantity)
           return self.model.predict(features)
           
       def _extract_features(self, asks, bids, quantity):
           return {
               'spread': (asks[0][0] - bids[0][0]) / bids[0][0],
               'imbalance': self._calculate_imbalance(asks, bids),
               'depth': self._calculate_depth(asks, bids),
               'quantity_ratio': quantity / self._total_volume(asks, bids)
           }
   ```

   b. **Market Impact Model**
   ```python
   class AlmgrenChrissModel:
       def __init__(self, volatility=0.02):
           self.volatility = volatility
           self.eta = 0.1  # Temporary impact
           self.gamma = 0.01  # Permanent impact
           
       def calculate_market_impact(self, quantity, price, time_horizon):
           # Temporary impact
           temp_impact = self.eta * (quantity/self.volume) * \
                        math.sqrt(quantity/time_horizon)
           
           # Permanent impact
           perm_impact = self.gamma * (quantity/self.volume)
           
           return temp_impact, perm_impact
   ```

## Performance Monitoring

### Metrics Collection
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'latency': [],
            'throughput': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def record_latency(self, start_time):
        latency = (time.time() - start_time) * 1000
        self.metrics['latency'].append(latency)
        if len(self.metrics['latency']) > 100:
            self.metrics['latency'].pop(0)
            
    def get_statistics(self):
        return {
            'avg_latency': np.mean(self.metrics['latency']),
            'p95_latency': np.percentile(self.metrics['latency'], 95),
            'throughput': self.metrics['throughput'],
            'error_rate': self.metrics['errors'] / self.metrics['throughput']
        }
```

### Performance Optimization Techniques

1. **Data Processing**
   - Queue-based architecture for non-blocking operations
   - Efficient data structures for orderbook management
   - Batch processing of updates
   - Memory-efficient feature calculation

2. **Model Calculations**
   - Incremental model updates
   - Efficient feature extraction
   - Optimized numerical computations
   - Memory-efficient data storage

3. **UI Updates**
   - Throttled updates (100ms interval)
   - Efficient rendering
   - Resource cleanup
   - Minimal UI thread blocking

## Error Handling

### WebSocket Error Recovery
```python
async def handle_websocket_error(self, error):
    if isinstance(error, websockets.exceptions.ConnectionClosed):
        logger.error("Connection closed, attempting to reconnect...")
        await self.reconnect()
    elif isinstance(error, asyncio.TimeoutError):
        logger.warning("Connection timeout, checking heartbeat...")
        if time.time() - self.last_message_time > self.heartbeat_interval:
            await self.reconnect()
    else:
        logger.error(f"Unexpected error: {error}")
        await self.reconnect()
```

### Data Validation
```python
def validate_orderbook(self, asks, bids):
    if not asks or not bids:
        raise ValueError("Empty orderbook")
        
    # Check price levels
    for price, qty in asks + bids:
        if price <= 0 or qty <= 0:
            raise ValueError(f"Invalid price/quantity: {price}, {qty}")
            
    # Check spread
    spread = (asks[0][0] - bids[0][0]) / bids[0][0]
    if spread > 0.01:  # 1% spread
        logger.warning(f"Large spread detected: {spread:.2%}")
```

## Future Improvements

### 1. Model Enhancements
- Integration with machine learning models
- Advanced market impact models
- Custom fee structures
- Real-time model adaptation

### 2. Performance Optimizations
- Parallel processing of orderbook updates
- GPU acceleration for model calculations
- Memory optimization for large orderbooks
- Network optimization for WebSocket connection

### 3. Feature Additions
- Multiple exchange support
- Custom trading strategies
- Historical data analysis
- Backtesting capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request



## Acknowledgments

- OKX for providing market data
- Almgren and Chriss for their market impact model
- PyQt5 team for the UI framework
- Python community for excellent libraries 