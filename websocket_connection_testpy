import asyncio
import websockets

async def test_ws():
    url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    async with websockets.connect(url) as ws:
        print("Connected!")
        try:
            while True:
                msg = await ws.recv()
                print(msg)
        except Exception as e:
            print("Connection closed:", e)

asyncio.run(test_ws())