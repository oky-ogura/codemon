from .models import AiConfig, Account

def global_character_data(request):
    """
    ログイン中ユーザーのAIキャラクター情報をテンプレートへ渡す
    セッションベースの認証とDjango認証の両方をサポート
    アクセサリー情報も含む
    """
    from codemon.models import UserAccessory
    
    context = {
        'ai_name': 'うたー',
        'character': 'inu',
        'appearance': 'イヌ.png',  # デフォルトのappearance追加
        'character_img': "/static/codemon/images/characters/イヌ.png",
        'equipped_accessory': None,
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

            
            # 装備中のアクセサリーを取得
            try:
                account = Account.objects.get(user_id=user_id)
                equipped = UserAccessory.objects.filter(
                    user=account,
                    is_equipped=True
                ).select_related('accessory').first()
                if equipped:
                    context['equipped_accessory'] = equipped
            except Exception as e:
                print(f"Accessory fetch error: {e}")
                

    except Exception as e:
        print(f"Context Processor Error: {e}")
    
    return context
