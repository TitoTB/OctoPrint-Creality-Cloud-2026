import time
import websocket
import threading
import json
import logging

class WebSocketConnectionException(Exception):
    pass

class WebSocketClient:

    def __init__(self, url, queue, token ,subprotocols=None, waitsecs=120):
        self._logger = logging.getLogger("octoprint.plugins.crealitycloud")
        self._mutex = threading.RLock()
        self._name = "xiongrui"
        self._id = "105199"
        self._user_agent = "crealitycloud"
        self._url = url 
        self._queue = queue
        self.reconnect_count = 0
        self._reconnecting = False
        self.subprotocols = subprotocols
        self.token = token

        self.ws = websocket.WebSocketApp(
            self._url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            #header=header,
            subprotocols=self.subprotocols
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

        for i in range(waitsecs * 10):  # Give it up to 120s for ws hand-shaking to finish
            if self.connected():
                return
            time.sleep(0.1)
        self.ws.close()
        raise WebSocketConnectionException(f'Not connected to websocket server after {waitsecs}s')

    def send(self, data, as_binary=False):
        self._logger.debug(f"send{data}")
        with self._mutex:
            if self.connected():
                if as_binary:
                    self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
                    self._logger.debug(f'send (binary){data}')
                else:
                    self.ws.send(data)

    def connected(self):
        with self._mutex:
            try:
                return self.ws and self.ws.sock and self.ws.sock.connected
            except AttributeError:
                return False

    def close(self):
        with self._mutex:
            try:
                ws = self.ws
                if ws:
                    ws.on_close = lambda *a: None
                    ws.on_error = lambda *a: None
                    ws.keep_running = False
                    ws.close()
            except Exception:
                pass
			
    def _reconnect(self, ws, reason):
        with self._mutex:
            if self._reconnecting:
                return
            self._reconnecting = True
        try:
            self.reconnect_count += 1
            delay = min(5 * self.reconnect_count, 60)
            self._logger.info(
                "WebSocket %s, reconnecting in %ds (attempt %d)...",
                reason, delay, self.reconnect_count,
            )
            self.close()
            time.sleep(delay)
            self.connection_tmp(ws)
        finally:
            with self._mutex:
                self._reconnecting = False

    def on_error(self, ws, error):
        if self._reconnecting:
            return
        self._logger.error(f"websocket error: {error}")
        self._reconnect(ws, f"error: {error}")

    def on_message(self, ws, msg):
        self.reconnect_count = 0
        self._logger.debug(f"recv: {msg}")
        parsed = json.loads(msg)
        action = parsed.get("action", "")
        if parsed.get("code") and parsed.get("code") != 0:
            self._logger.warning(f"signaling error: code={parsed.get('code')} msg={parsed.get('errMsg')}")
        if action == "ice_msg":
            self._logger.debug(f"signaling: {parsed.get('sdpMessage', {}).get('type', '?')} from {parsed.get('from', '?')[:12]}")
        if action != "join":
            self._queue.put(msg)

    def on_close(self, ws, status, msg):
        self._logger.info(f"WebSocket closed: status={status} msg={msg}")
        if not self._reconnecting:
            self._reconnect(ws, f"closed (status={status})")

    def on_open(self, ws):
        data = {
            "action": "join",
            "to": "server",
            "clientCtx": {
                "device_brand": "raspberry",
                "os_version": "linux",
                "platform_type": 1,
                "app_version": "v1.1.2"
            },
            "token": {
                "jwtToken": self.token
            }
        }
        try:
            ws.send(json.dumps(data))
        except Exception:
            self._logger.debug("WebSocket send failed in on_open, connection already dead.")

    def connection_tmp(self, ws):
        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp(            
            self._url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            subprotocols=self.subprotocols)
        
        ws.on_open = self.on_open
        self.ws = ws
        try:
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start() 
        except KeyboardInterrupt:
            ws.close()  
        except:
            ws.close() 

    def token_update(self, token):
        self.token = str(token)
