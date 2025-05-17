# src/websocket/orderbook_client.py

import asyncio
import json
import logging
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderbookClient:
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback
        self.running = True

    async def connect(self):
        while self.running:
            try:
                async with websockets.connect(self.url) as ws:
                    self.ws = ws
                    logger.info(f"Connected to {self.url}")
                    while self.running:
                        try:
                            message = await ws.recv()
                            data = json.loads(message)
                            self.callback(data)
                        except websockets.exceptions.ConnectionClosed:
                            logger.error("Connection closed, attempting to reconnect...")
                            break
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            break
            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(2)