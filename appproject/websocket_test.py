import asyncio
import websockets
import json
import logging
from urllib.parse import urlparse

# =======================================
# 🧩 ロギング設定
# =======================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket_test")

# =======================================
# ⚙️ WebSocket テスト関数
# =======================================
async def test_websocket():
    uri = "ws://localhost:8001/ws/chat/1/"
    headers = {
        "Origin": "http://localhost:8001",
        "Host": "localhost:8001",
        "User-Agent": "WebSocket-Test-Client",
        "Cookie": "sessionid=test-session-id; csrftoken=test-csrf-token",
    }

    logger.info(f"接続試行中: {uri}")
    parsed_uri = urlparse(uri)
    logger.debug(f"解析したURI: scheme={parsed_uri.scheme}, netloc={parsed_uri.netloc}, path={parsed_uri.path}")

    try:
        async with websockets.connect(
            uri,
            ping_interval=None,  # Django Channelsでは無効にしてもOK
            ping_timeout=None,
            close_timeout=5,
            extra_headers=headers,
        ) as websocket:
            logger.info("✅ 接続成功！")

            # テストメッセージを送信
            test_message = {
                "action": "send",
                "content": "テストメッセージ",
                "sender_id": 1
            }
            await websocket.send(json.dumps(test_message))
            logger.info(f"📤 送信: {test_message}")

            # サーバーからの初回レスポンス受信
            response = await websocket.recv()
            logger.info(f"📩 受信: {response}")

            # 永続ループ（新しいメッセージを待機）
            while True:
                try:
                    message = await websocket.recv()
                    logger.info(f"💬 新しいメッセージ受信: {message}")
                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"🔌 接続が閉じられました（コード: {e.code}, 理由: {e.reason}）")
                    break

    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"❌ 無効なステータスコード: {e.status_code}")
    except websockets.exceptions.InvalidHandshake as e:
        logger.error(f"🤝 WebSocketハンドシェイクエラー: {e}")
    except ConnectionRefusedError:
        logger.error("🚫 接続が拒否されました。サーバーが起動中か確認してください。")
    except Exception as e:
        logger.exception(f"⚠️ 予期しないエラー: {e}")

# =======================================
# 🚀 実行部分（Python 3.13対応）
# =======================================
if __name__ == "__main__":
    asyncio.run(test_websocket())
