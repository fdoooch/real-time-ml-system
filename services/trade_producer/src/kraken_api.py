from typing import Dict
from websocket import create_connection, WebSocket
import json
import datetime


def convert_datetime_to_timestamp_in_ms(dt_str: str) -> int:
    dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    # Convert to Unix timestamp in milliseconds
    timestamp_ms = int(dt.timestamp() * 1000)
    return timestamp_ms

class KrakenWebsocketTradeAPI:
    URL = "wss://ws.kraken.com/v2"

    def __init__(self, symbol: str):
        self.symbol = f"{symbol.split('USDT')[0]}/USDT"
        self._ws = self._subscribe_to_trades()

    
    def _subscribe_to_trades(self) -> WebSocket:
        """
        Establishes a connection to the Kraken websocket API
        """
        ws = create_connection(self.URL)
        # subscribe to trades
        msg = {
            "method": "subscribe",
            "params": {
                "channel": "trade",
                "symbol": [
                    self.symbol,
                ],
                "snapshot": False
            }
        }
        ws.send(json.dumps(msg))

        # wait for subscription confirmation
        for i in range(5):
            msg = ws.recv()
            print(f"Received message: {msg}")
            msg_json = json.loads(msg)
            if msg_json.get("method") == "subscribe" and msg_json.get("success"):
                print("Connected to websocket")
                return ws
        print("Could not connect to websocket")
        return None
        

    def get_trades(self) -> list[Dict]:
        # mock_trades = [
        #     {
        #         "symbol": "BTCUSDT",
        #         "price": 60000,
        #         "volume": 0.01,ex
        #         "time": 1663975000000
        #     },
        #     {
        #         "symbol": "BTCUSDT",
        #         "price": 59000,
        #         "volume": 0.02,
        #         "time": 1663976000000
        #     }
        # ]
        msg =self._ws.recv()
        print(f"Received message: {msg}")
        if '"heartbeat"' in msg:
            return []
        msg_json = json.loads(msg)
        if msg_json.get("channel") == "trade":
                trades = []
                for trade in msg_json.get("data"):
                    trades.append(
                        {
                            "symbol": trade.get("symbol"),
                            "price": trade.get("price"),
                            "qty": trade.get("qty"),
                            "timestamp": convert_datetime_to_timestamp_in_ms(trade.get("timestamp"))
                        }
                    )
                return trades
        print("Unknown websocket message format")
        return msg