"""
Custom authentication middleware for Channels WebSocket
"""
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from accounts.models import Account
import logging

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_account_from_scope(scope):
    """scopeからAccountオブジェクトを取得"""
    try:
        # scopeからsessionオブジェクトを取得
        session = scope.get('session')
        
        if not session:
            logger.debug("No session in scope")
            return None
            
        # Lazy objectの場合は実体化
        if hasattr(session, '_wrapped'):
            if session._wrapped is None:
                session._setup()
            session = session._wrapped
        
        # セッションからaccount_user_idを取得
        account_user_id = session.get('account_user_id')
        logger.debug(f"Session account_user_id: {account_user_id}")
        
        if account_user_id:
            try:
                account = Account.objects.get(user_id=account_user_id)
                logger.debug(f"Found account: {account.user_name} (ID: {account.user_id})")
                return account
            except Account.DoesNotExist:
                logger.warning(f"Account with user_id {account_user_id} not found")
        else:
            logger.debug("No account_user_id in session")
    except Exception as e:
        logger.error(f"Error getting account from scope: {e}", exc_info=True)
    
    return None


class AccountAuthMiddleware:
    """
    カスタム認証ミドルウェア
    セッションからAccountユーザーを取得してscopeに設定
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        logger.debug("AccountAuthMiddleware called")
        
        # WebSocket接続の場合のみ処理
        if scope['type'] == 'websocket':
            # セッションからAccountを取得
            account = await get_account_from_scope(scope)
            
            if account:
                # Accountオブジェクトに is_authenticated 属性を追加
                account.is_authenticated = True
                scope['user'] = account
                scope['account'] = account
                logger.debug(f"User authenticated: {account.user_name}")
            else:
                # すでにuserがAnonymousUserでない場合は上書きしない
                if 'user' not in scope or not hasattr(scope['user'], 'is_authenticated'):
                    scope['user'] = AnonymousUser()
                logger.debug(f"Authentication failed, user: {scope.get('user')}")
        
        return await self.app(scope, receive, send)


def AccountAuthMiddlewareStack(inner):
    """
    Accountベースの認証ミドルウェアスタック
    """
    from channels.auth import AuthMiddlewareStack
    # AccountAuthMiddlewareを先に内側に配置し、
    # AuthMiddlewareStackを外側に配置することで、
    # AuthMiddlewareStackが先に実行されてsessionをscopeに追加する
    return AuthMiddlewareStack(AccountAuthMiddleware(inner))

