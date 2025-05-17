# src/main.py
import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QLabel, QStatusBar
from PyQt5.QtCore import Qt, QTimer
from ui.main_window import MainWindow
from websocket.orderbook_client import OrderbookClient
from models.market_impact import AlmgrenChrissModel
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
        self.market_impact_model = AlmgrenChrissModel(volatility=0.02)
        self.data_queue = queue.Queue()
        
        # Set up WebSocket connection
        self.setup_websocket()
        
        # Set up update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # Update every 100ms

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
                print("WebSocket thread error:", e)
                traceback.print_exc()
        
        thread = threading.Thread(target=run_websocket, daemon=True)
        thread.start()

    def process_orderbook_data(self, data: dict):
        # print("Received data in callback:", type(data), data)
        self.data_queue.put(data)

    def update_ui(self):
        # print("update_ui called")
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                # print("Updating UI with data:", type(data), data)
                # If data is a list, get the first element
                if isinstance(data, list) and data:
                    data = data[0]
                asks = data.get('asks', [])
                bids = data.get('bids', [])
                
                # Calculate metrics
                slippage = self.calculate_slippage(asks, bids)
                fees = self.calculate_fees()
                impact = self.calculate_market_impact()
                
                # Update UI
                self.window.update_outputs({
                    'slippage': f"{slippage:.4f}%",
                    'fees': f"${fees:.2f}",
                    'impact': f"${impact:.2f}",
                    'net_cost': f"${(slippage + fees + impact):.2f}",
                    'maker_taker': "0.65/0.35",  # Example ratio
                    'latency': "5"  # Example latency in ms
                })
        except Exception as e:
            import traceback
            print("Error updating UI:", e)
            traceback.print_exc()

    def calculate_slippage(self, asks, bids) -> float:
        """Calculate expected slippage based on orderbook data"""
        return 0.1  # Example value

    def calculate_fees(self) -> float:
        """Calculate expected fees based on fee tier"""
        return 0.5  # Example value

    def calculate_market_impact(self) -> float:
        """Calculate market impact using Almgren-Chriss model"""
        return 1.2  # Example value

    def run(self):
        self.window.show()
        return self.app.exec()

if __name__ == "__main__":
    simulator = TradeSimulator()
    sys.exit(simulator.run())