# src/websocket/orderbook_client.py

import asyncio
import json
import logging
import websockets
import time
from typing import Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderbookClient:
    def __init__(self, url: str, callback: Callable):
        self.url = url
        self.callback = callback
        self.running = True
        self.reconnect_delay = 1.0
        self.max_reconnect_delay = 30.0
        self.last_message_time = 0
        self.heartbeat_interval = 30  # seconds
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

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
                    logger.info(f"Connected to {self.url}")
                    self.reconnect_delay = 1.0  # Reset delay on successful connection
                    self.last_message_time = time.time()

                    while self.running:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=self.heartbeat_interval)
                            self.last_message_time = time.time()
                            
                            try:
                                data = json.loads(message)
                                self.callback(data)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse message: {e}")
                                continue
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                                continue

                        except asyncio.TimeoutError:
                            # Check if we've exceeded the heartbeat interval
                            if time.time() - self.last_message_time > self.heartbeat_interval:
                                logger.warning("No messages received within heartbeat interval")
                                break
                            continue
                        except websockets.exceptions.ConnectionClosed:
                            logger.error("Connection closed, attempting to reconnect...")
                            break
                        except Exception as e:
                            logger.error(f"Unexpected error: {e}")
                            break

            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(self.reconnect_delay)
                # Exponential backoff with max delay
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)

    async def close(self):
        """Gracefully close the WebSocket connection"""
        self.running = False
        if self.ws:
            await self.ws.close()