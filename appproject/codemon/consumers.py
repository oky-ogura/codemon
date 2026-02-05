import logging
import json
import os
import mimetypes
import base64
import asyncio
import httpx
from django.conf import settings
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from accounts.models import Account
from codemon.models import ChatThread, ChatMessage, ChatAttachment

# ロギング設定
logger = logging.getLogger('django.channels.consumer')
logger.setLevel(logging.DEBUG)

# エラー定数
WS_ERROR_NO_THREAD = 4000  # Thread IDがない
WS_ERROR_AUTH = 4001       # 認証エラー
WS_ERROR_INVALID_JSON = 4002  # 無効なJSON
WS_ERROR_INTERNAL = 4003   # 内部エラー


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocketチャットコンシューマー
    
    このクラスは、WebSocketを使用したリアルタイムチャット機能を実装します。
    主な機能：
    - WebSocket接続の確立と切断
    - メッセージの送受信
    - ファイルのアップロード
    - メッセージの既読管理
    - AI応答の生成と送信
    """
    
    def __init__(self, *args, **kwargs):
        """初期化
        
        Args:
            *args: 可変位置引数
            **kwargs: 可変キーワード引数
        """
        super().__init__(*args, **kwargs)
        self.thread_id = None  # チャットスレッドID
        self.group_name = None  # グループ名
        self.channel_layer = get_channel_layer()  # チャンネルレイヤー
        
    async def connect(self):
        """WebSocket接続確立時の処理"""
        logger.debug("新しい接続要求を受信")
        logger.debug(f"Scope: {self.scope}")
        
        self.thread_id = self.scope['url_route']['kwargs'].get('thread_id')
        logger.debug(f"Thread ID: {self.thread_id}")
        
        if self.thread_id is None:
            logger.error("Thread IDが見つかりません")
            await self.close()
            return

        self.group_name = f'chat_{self.thread_id}'
        logger.debug(f"Group Name: {self.group_name}")

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        logger.debug("グループに参加")
        
        # Accept the connection
        await self.accept()
        logger.info(f"WebSocket接続を確立: thread_id={self.thread_id}")

    async def disconnect(self, close_code):
        """WebSocket切断時の処理"""
        logger.info(f"WebSocket切断: thread_id={self.thread_id}, code={close_code}")
        
        # Leave room group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.debug("グループから離脱")

    async def receive(self, text_data=None, bytes_data=None):
        """クライアントからメッセージを受信したときの処理
        
        Args:
            text_data (str, optional): 受信したテキストデータ
            bytes_data (bytes, optional): 受信したバイナリデータ
        """
        # 入力検証
        if text_data is None and bytes_data is None:
            logger.warning("空のメッセージを受信")
            return

        # JSON解析
        try:
            data = json.loads(text_data if text_data else bytes_data.decode())
            logger.debug(f"受信データをパース: {data}")
        except json.JSONDecodeError as e:
            error_msg = f"JSONパースエラー: {str(e)}"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INVALID_JSON
            }))
            return
        except Exception as e:
            error_msg = f"メッセージ処理エラー: {str(e)}"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INTERNAL
            }))
            return

        # 認証チェック
        user = self.scope.get('user')
        logger.debug(f"User from scope: {user}, is_authenticated: {getattr(user, 'is_authenticated', False)}")
        logger.debug(f"Scope keys: {self.scope.keys()}")
        logger.debug(f"Session: {self.scope.get('session')}")
        
        if not user or not user.is_authenticated:
            error_msg = "認証が必要です"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_AUTH
            }))
            return

        # アクションの取得と検証
        action = data.get('action')
        if not action:
            error_msg = "アクションが指定されていません"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INVALID_JSON
            }))
            return

        # アクションに応じた処理
        try:
            if action == 'send':
                await self.handle_send_message(data, user)
            elif action == 'mark_read':
                await self.handle_mark_read(data, user)
            else:
                error_msg = f"不明なアクション: {action}"
                logger.error(error_msg)
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': error_msg,
                    'code': WS_ERROR_INVALID_JSON
                }))
        except Exception as e:
            error_msg = f"アクション処理エラー: {str(e)}"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INTERNAL
            }))

    async def handle_send_message(self, data, user):
        """メッセージ送信処理
        
        Args:
            data (dict): 受信データ
            user (User): 認証済みユーザー
        """
        # 入力データの取得
        content = data.get('content', '').strip()
        attachments = data.get('attachments', [])

        # 入力バリデーション
        if not content and not attachments:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'メッセージまたはファイルを入力してください',
                'code': WS_ERROR_INVALID_JSON
            }))
            return

        try:
            # メッセージを保存
            saved = await self.create_message(user.user_id, content, attachments)

            # グループにブロードキャスト
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': saved,
                }
            )

            # AI応答の処理（設定が有効な場合）
            if hasattr(settings, 'AI_API_KEY') and settings.AI_API_KEY:
                asyncio.create_task(self.handle_ai_response(content))

        except Exception as e:
            error_msg = f"メッセージ送信エラー: {str(e)}"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INTERNAL
            }))

    async def handle_mark_read(self, data, user):
        """メッセージ既読処理
        
        Args:
            data (dict): 受信データ
            user (User): 認証済みユーザー
        """
        # メッセージIDの取得
        message_ids = data.get('message_ids', [])
        if not message_ids:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'メッセージIDが指定されていません',
                'code': WS_ERROR_INVALID_JSON
            }))
            return

        try:
            # 既読状態を保存
            await self.mark_messages_as_read(message_ids, user.user_id)
            
            # 既読情報を送信
            for message_id in message_ids:
                readers = await self.get_message_readers(message_id)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'chat.read_receipt',
                        'message_id': message_id,
                        'readers': readers
                    }
                )
        except Exception as e:
            error_msg = f"既読処理エラー: {str(e)}"
            logger.error(error_msg)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error_msg,
                'code': WS_ERROR_INTERNAL
            }))

    async def chat_message(self, event):
        """メッセージをWebSocketに送信
        
        Args:
            event (dict): 送信イベントデータ
        """
        try:
            message = event['message']
            await self.send(text_data=json.dumps({
                'type': 'chat.message',
                'message': message
            }))
        except Exception as e:
            logger.error(f"メッセージ送信エラー: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'メッセージの送信に失敗しました',
                'code': WS_ERROR_INTERNAL
            }))

    async def chat_read_receipt(self, event):
        """既読情報をWebSocketに送信
        
        Args:
            event (dict): 既読イベントデータ
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat.read_receipt',
                'message_id': event['message_id'],
                'readers': event['readers']
            }))
        except Exception as e:
            logger.error(f"既読情報送信エラー: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': '既読情報の送信に失敗しました',
                'code': WS_ERROR_INTERNAL
            }))

    async def chat_score(self, event):
        """点数付与情報をWebSocketに送信
        
        Args:
            event (dict): スコアイベントデータ
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat.score',
                'score': event['score']
            }))
        except Exception as e:
            logger.error(f"スコア情報送信エラー: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'スコア情報の送信に失敗しました',
                'code': WS_ERROR_INTERNAL
            }))

    async def chat_delete(self, event):
        """メッセージ削除通知をWebSocketに送信
        
        Args:
            event (dict): 削除イベントデータ
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat.delete',
                'message_id': event.get('message_id'),
                'deleted_by_id': event.get('deleted_by_id'),
                'deleted_by_name': event.get('deleted_by_name'),
                'deleted_at': event.get('deleted_at')
            }))
        except Exception as e:
            logger.error(f"削除通知送信エラー: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': '削除通知の送信に失敗しました',
                'code': WS_ERROR_INTERNAL
            }))

    @database_sync_to_async
    def mark_messages_as_read(self, message_ids, reader_id):
        """メッセージを既読としてマーク
        
        Args:
            message_ids (list): 既読マークするメッセージIDのリスト
            reader_id (int): 読者のユーザーID
            
        Returns:
            bool: 既読マークの成功/失敗
        """
        try:
            # 必要なモデルをインポート
            now = timezone.now()

            # 読者を取得
            try:
                reader = Account.objects.get(user_id=reader_id)
            except Account.DoesNotExist:
                logger.error(f"読者が見つかりません: {reader_id}")
                return False

            # メッセージを取得
            messages = ChatMessage.objects.filter(message_id__in=message_ids)
            if not messages.exists():
                logger.warning(f"既読マーク対象のメッセージが見つかりません: {message_ids}")
                return False

            # 既読レコードを一括作成（既存の既読は無視）
            from .models import ReadReceipt
            receipts = []
            for msg in messages:
                if not ReadReceipt.objects.filter(message=msg, reader=reader).exists():
                    receipts.append(ReadReceipt(
                        message=msg,
                        reader=reader,
                        read_at=now
                    ))

            if receipts:
                ReadReceipt.objects.bulk_create(receipts)
                logger.info(f"{len(receipts)}件のメッセージを既読マークしました: {message_ids}")
            else:
                logger.info("新規の既読マークはありません")

            return True

        except Exception as e:
            logger.error(f"既読マークエラー: {str(e)}")
            return False

    @database_sync_to_async
    def get_message_readers(self, message_id):
        """メッセージの既読者一覧を取得
        
        Args:
            message_id: メッセージID
            
        Returns:
            list: 既読者情報のリスト
        """
        try:
            from .models import ChatMessage
            message = ChatMessage.objects.get(message_id=message_id)
            readers = []
            
            for receipt in message.read_receipts.select_related('reader').all():
                readers.append({
                    'id': receipt.reader.user_id,
                    'name': receipt.reader.user_name,
                    'read_at': receipt.read_at.isoformat()
                })
            
            return readers
            
        except ChatMessage.DoesNotExist:
            logger.error(f"メッセージが見つかりません: {message_id}")
            return []
        except Exception as e:
            logger.error(f"既読者一覧取得エラー: {str(e)}")
            return []

    @database_sync_to_async
    def create_message(self, sender_id, content, attachments=None):
        """新しいメッセージを作成
        
        Args:
            sender_id (int): 送信者のユーザーID
            content (str): メッセージ内容
            attachments (list, optional): 添付ファイルのリスト
            
        Returns:
            dict: 作成されたメッセージの情報
        """
        try:
            # スレッドの取得または作成
            thread, _ = ChatThread.objects.get_or_create(
                thread_id=self.thread_id,
                defaults={
                    'title': f'Thread {self.thread_id}',
                    'created_by_id': sender_id
                }
            )

            # 送信者の取得
            try:
                sender = Account.objects.get(user_id=sender_id)
            except Account.DoesNotExist:
                logger.warning(f"送信者が見つかりません。スレッド作成者を使用: {sender_id}")
                sender = thread.created_by

            # メッセージの作成
            msg = ChatMessage.objects.create(
                thread=thread,
                sender=sender,
                content=content
            )

            # 添付ファイルの処理
            message_attachments = []
            if attachments:
                for attachment in attachments:
                    try:
                        # ChatAttachmentモデルに保存
                        chat_attachment = ChatAttachment.objects.create(
                            message=msg,
                            file=attachment['file']
                        )
                        message_attachments.append({
                            'id': chat_attachment.attachment_id,
                            'url': chat_attachment.file.url,
                            'filename': os.path.basename(chat_attachment.file.name),
                            'mime_type': mimetypes.guess_type(chat_attachment.file.name)[0]
                        })
                    except Exception as e:
                        logger.error(f"添付ファイル処理エラー: {str(e)}")
                        continue

            # メッセージ情報を返却
            return {
                'message_id': msg.message_id,
                'thread_id': thread.thread_id,
                'sender_id': sender.user_id,
                'sender_name': getattr(sender, 'user_name', ''),
                'sender_avatar': sender.avatar.url if sender.avatar else None,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'attachments': message_attachments
            }

        except Exception as e:
            logger.error(f"メッセージ作成エラー: {str(e)}")
            raise

    async def fetch_ai_reply(self, prompt: str) -> str | None:
        """OpenAI APIを使用してAI応答を取得
        
        Args:
            prompt (str): ユーザーのメッセージ
            
        Returns:
            str | None: AI応答テキスト。エラー時はNone。
        """
        try:
            # API設定の取得
            api_key = getattr(settings, 'AI_API_KEY', '')
            model = getattr(settings, 'AI_MODEL', 'gpt-3.5-turbo')
            
            if not api_key:
                logger.warning("AI APIキーが設定されていません")
                return None

            # APIリクエストの準備
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 512,
                'temperature': 0.7,
            }

            # APIリクエストの送信
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                # レスポンスの処理
                if response.status_code == 200:
                    try:
                        body = response.json()
                        return body['choices'][0]['message']['content']
                    except (KeyError, IndexError) as e:
                        logger.error(f"APIレスポンスの解析エラー: {str(e)}")
                        return None
                else:
                    logger.error(f"API呼び出しエラー: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"AI応答取得エラー: {str(e)}")
            return None

    @database_sync_to_async
    def create_ai_message(self, ai_text: str):
        """AI応答メッセージを作成
        
        Args:
            ai_text (str): AI応答テキスト
            
        Returns:
            dict: 作成されたAIメッセージの情報
        """
        try:
            # AIアカウントの取得または作成
            ai_account, _ = Account.objects.get_or_create(
                email='ai@local',
                defaults={
                    'user_name': 'AI',
                    'password': 'ai'
                }
            )
            
            # スレッドの取得
            try:
                thread = ChatThread.objects.get(thread_id=self.thread_id)
            except ChatThread.DoesNotExist:
                logger.error(f"スレッドが見つかりません: {self.thread_id}")
                raise

            # メッセージの作成
            msg = ChatMessage.objects.create(
                thread=thread,
                sender=ai_account,
                content=ai_text
            )

            # メッセージ情報を返却
            return {
                'message_id': msg.message_id,
                'thread_id': thread.thread_id,
                'sender_id': ai_account.user_id,
                'sender_name': 'AI',
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'is_ai': True
            }

        except Exception as e:
            logger.error(f"AIメッセージ作成エラー: {str(e)}")
            raise
