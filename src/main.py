# src/main.py
import sys
import asyncio
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QLabel, QStatusBar, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from ui.main_window import MainWindow
from websocket.orderbook_client import OrderbookClient
from models.market_impact import AlmgrenChrissModel
from models.slippage import SlippageModel
from models.fee_calculator import FeeCalculator
from models.maker_taker import MakerTakerPredictor
import threading
import queue
import traceback
import websockets
import json
from logger import setup_logger

logger = setup_logger()

class TradeSimulator:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.orderbook_client = None
        
        # Initialize models
        self.market_impact_model = AlmgrenChrissModel(volatility=0.02)
        self.slippage_model = SlippageModel()
        self.fee_calculator = FeeCalculator()
        self.maker_taker_predictor = MakerTakerPredictor()
        
        # Data structures
        self.data_queue = queue.Queue()
        self.latency_measurements = []
        self.performance_metrics = {
            'total_messages': 0,
            'processed_messages': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
        # Set up WebSocket connection
        self.setup_websocket()
        
        # Set up update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Update every 100ms
        
        # Set up cleanup
        self.app.aboutToQuit.connect(self.cleanup)

    def cleanup(self):
        """Cleanup resources before application exit"""
        logger.info("Cleaning up resources...")
        if self.orderbook_client:
            self.orderbook_client.running = False
            # Wait for WebSocket thread to finish
            time.sleep(0.5)
        
        # Log final performance metrics
        runtime = time.time() - self.performance_metrics['start_time']
        logger.info(f"Performance Summary:")
        logger.info(f"Runtime: {runtime:.2f} seconds")
        logger.info(f"Total Messages: {self.performance_metrics['total_messages']}")
        logger.info(f"Processed Messages: {self.performance_metrics['processed_messages']}")
        logger.info(f"Error Rate: {(self.performance_metrics['errors'] / self.performance_metrics['total_messages'] * 100):.2f}%")
        logger.info(f"Average Latency: {self.calculate_latency():.2f}ms")

    def setup_websocket(self):
        url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
        self.orderbook_client = OrderbookClient(url, self.process_orderbook_data)
        self.orderbook_client.running = True
        
        # Start WebSocket connection in a separate thread
        def run_websocket():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.orderbook_client.connect())
            except Exception as e:
                logger.error(f"WebSocket thread error: {e}")
                traceback.print_exc()
                QMessageBox.critical(self.window, "Connection Error",
                                   "Failed to connect to WebSocket server. Please check your internet connection and try again.")
        
        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()

    def process_orderbook_data(self, data: dict):
        start_time = time.time()
        self.performance_metrics['total_messages'] += 1
        
        try:
            # Validate orderbook data
            if not data.get('asks') or not data.get('bids'):
                logger.warning("Received empty orderbook data")
                return
                
            # Convert string values to float and validate price levels
            asks = []
            bids = []
            
            for price, qty in data.get('asks', []):
                try:
                    price_float = float(price)
                    qty_float = float(qty)
                    if price_float > 0 and qty_float > 0:
                        asks.append((price_float, qty_float))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid ask level: {price}, {qty}")
                    continue
                    
            for price, qty in data.get('bids', []):
                try:
                    price_float = float(price)
                    qty_float = float(qty)
                    if price_float > 0 and qty_float > 0:
                        bids.append((price_float, qty_float))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid bid level: {price}, {qty}")
                    continue
            
            # Sort orderbook levels
            asks.sort(key=lambda x: x[0])
            bids.sort(key=lambda x: x[0], reverse=True)
            
            # Validate orderbook structure
            if not asks or not bids:
                logger.warning("No valid orderbook levels after processing")
                return
                
            # Check for reasonable price spread and gaps
            best_ask = asks[0][0]
            best_bid = bids[0][0]
            spread = (best_ask - best_bid) / best_bid
            
            # Check for large price gaps in asks
            for i in range(1, len(asks)):
                gap = (asks[i][0] - asks[i-1][0]) / asks[i-1][0]
                if gap > 0.01:  # More than 1% gap
                    logger.warning(f"Large price gap detected in asks: {gap:.2%} between {asks[i-1][0]} and {asks[i][0]}")
                    # Remove the outlier level
                    asks.pop(i)
                    break
            
            # Check for large price gaps in bids
            for i in range(1, len(bids)):
                gap = (bids[i-1][0] - bids[i][0]) / bids[i-1][0]
                if gap > 0.01:  # More than 1% gap
                    logger.warning(f"Large price gap detected in bids: {gap:.2%} between {bids[i-1][0]} and {bids[i][0]}")
                    # Remove the outlier level
                    bids.pop(i)
                    break
            
            if spread > 0.01:  # More than 1% spread
                logger.warning(f"Unusually large spread detected: {spread:.2%}")
            
            # Update models
            try:
                quantity = float(self.window.quantity_input.text())
                self.slippage_model.update(asks, bids, quantity)
            except ValueError as e:
                logger.error(f"Invalid quantity value: {e}")
                return
            
            # Calculate latency
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.latency_measurements.append(latency)
            if len(self.latency_measurements) > 100:
                self.latency_measurements.pop(0)
                
            # Add latency to data
            data['processing_latency'] = latency
            data['asks'] = asks
            data['bids'] = bids
            
            self.data_queue.put(data)
            self.performance_metrics['processed_messages'] += 1
            
        except Exception as e:
            logger.error(f"Unexpected error in process_orderbook_data: {e}")
            traceback.print_exc()
            self.performance_metrics['errors'] += 1

    def update_ui(self):
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                
                # If data is a list, get the first element
                if isinstance(data, list) and data:
                    data = data[0]
                
                asks = data.get('asks', [])
                bids = data.get('bids', [])
                
                if not asks or not bids:
                    continue
                
                # Get input parameters with validation
                try:
                    quantity = float(self.window.quantity_input.text())
                    if quantity <= 0:
                        logger.warning("Invalid quantity: must be positive")
                        continue
                        
                    fee_tier = int(self.window.fee_combo.currentText().split()[-1])
                    if fee_tier not in [1, 2, 3]:
                        logger.warning(f"Invalid fee tier: {fee_tier}")
                        continue
                        
                    volatility = float(self.window.volatility_input.text())
                    if not 0 <= volatility <= 1:
                        logger.warning(f"Invalid volatility: {volatility}")
                        continue
                except ValueError as e:
                    logger.error(f"Invalid input value: {e}")
                    continue
                
                # Calculate metrics
                slippage = self.calculate_slippage(asks, bids, quantity)
                fees = self.calculate_fees(asks, bids, quantity, fee_tier)
                impact = self.calculate_market_impact(asks, bids, quantity, volatility)
                maker_taker = self.calculate_maker_taker(asks, bids)
                latency = self.calculate_latency()
                
                # Update UI
                self.window.update_outputs({
                    'slippage': f"{slippage:.4f}%",
                    'fees': f"${fees:.2f}",
                    'impact': f"${impact:.2f}",
                    'net_cost': f"${(slippage + fees + impact):.2f}",
                    'maker_taker': f"{maker_taker:.2f}/{1-maker_taker:.2f}",
                    'latency': f"{latency:.1f}"
                })
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
            traceback.print_exc()

    def calculate_slippage(self, asks, bids, quantity):
        """Calculate expected slippage based on orderbook data"""
        return self.slippage_model.predict_slippage(asks, bids, quantity)

    def calculate_fees(self, asks, bids, quantity, fee_tier):
        """Calculate expected fees based on fee tier"""
        if not asks or not bids:
            return 0.0
            
        # Get mid price from the closest levels
        best_ask = asks[0][0]
        best_bid = bids[0][0]
        
        # Check for reasonable price spread
        spread = (best_ask - best_bid) / best_bid
        if spread > 0.01:  # More than 1% spread
            logger.warning(f"Large spread detected: {spread:.2%}, using best bid price for fee calculation")
            price = best_bid  # Use best bid price for more conservative estimate
        else:
            price = (best_ask + best_bid) / 2
            
        # Calculate fees
        fee_amount, _ = self.fee_calculator.calculate_fees(
            order_type='market',
            quantity=quantity,
            price=price,
            fee_tier=fee_tier
        )
        return fee_amount

    def calculate_market_impact(self, asks, bids, quantity, volatility):
        """Calculate market impact using Almgren-Chriss model"""
        if not asks or not bids:
            return 0.0
            
        price = (float(asks[0][0]) + float(bids[0][0])) / 2
        self.market_impact_model.volatility = volatility
        temp_impact, perm_impact = self.market_impact_model.calculate_market_impact(
            quantity=quantity,
            price=price,
            time_horizon=1.0  # 1 day horizon
        )
        return (temp_impact + perm_impact) * price

    def calculate_maker_taker(self, asks, bids):
        """Calculate maker/taker proportion"""
        return self.maker_taker_predictor.predict_proportion(asks, bids)

    def calculate_latency(self):
        """Calculate average processing latency"""
        if not self.latency_measurements:
            return 0.0
        return sum(self.latency_measurements) / len(self.latency_measurements)

    def run(self):
        self.window.show()
        return self.app.exec()

if __name__ == "__main__":
    simulator = TradeSimulator()
    sys.exit(simulator.run())