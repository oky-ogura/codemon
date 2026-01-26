from .models import AiConfig, Account

def global_character_data(request):
    """
    ログイン中ユーザーのAIキャラクター情報をテンプレートへ渡す
    セッションベースの認証とDjango認証の両方をサポート
    """
    context = {
        'ai_name': 'うたー',
        'character': 'inu',
        'character_img': "/static/codemon/images/characters/イヌ.png"
    }
    
    
    try:
        # まずセッションベースの認証をチェック
        account = None
        user_id = None
        
        if request.session.get('is_account_authenticated'):
            user_id = request.session.get('account_user_id')
            if user_id:
                account = Account.objects.filter(user_id=user_id).first()
        # 次にDjango認証をチェック
        elif request.user.is_authenticated:
            account = Account.objects.filter(email=request.user.email).first()
            user_id = account.user_id if account else None
        
        # Account情報をコンテキストに追加（通知ボタンなどで使用）
        if account:
            context['account'] = account
        
        if user_id:
            # 最新のAiConfig取得
            ai_config = AiConfig.objects.filter(user_id=user_id).order_by('-created_at').first()
            if ai_config:
                context['ai_name'] = ai_config.ai_name or 'うたー'
                # appearanceをキャラクター画像名として利用（例: 'イヌ.png'）
                appearance = ai_config.appearance if ai_config.appearance else 'イヌ.png'
                context['character'] = appearance
                context['appearance'] = appearance
                context['character_img'] = f"/static/codemon/images/characters/{appearance}"
            else:
                context['ai_name'] = 'うたー'
                context['character'] = 'イヌ.png'
                context['character_img'] = "/static/codemon/images/characters/イヌ.png"
    except Exception as e:
        print(f"Context Processor Error: {e}")
    
    return context
