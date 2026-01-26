from .models import AiConfig, Account

def global_character_data(request):
    """
    ログイン中ユーザーのAIキャラクター情報をテンプレートへ渡す
    """
    if not request.user.is_authenticated:
        return {}

    context = {}
    try:
        # AccountモデルからユーザーID取得
        account = Account.objects.filter(email=request.user.email).first()
        user_id = account.user_id if account else None

        # Account情報をコンテキストに追加（通知ボタンなどで使用）
        context['account'] = account

        # 最新のAiConfig取得
        ai_config = AiConfig.objects.filter(user_id=user_id).order_by('-created_at').first()
        if ai_config:
            context['ai_name'] = ai_config.ai_name or 'うたー'
            # appearanceをキャラクターIDとして利用（例: 'inu', 'neko'）
            character_id = ai_config.appearance if ai_config.appearance else 'inu'
            context['character'] = character_id
            context['character_img'] = f"/static/codemon/images/characters/{character_id}.png"
        else:
            context['ai_name'] = 'うたー'
            context['character'] = 'inu'
            context['character_img'] = "/static/codemon/images/characters/inu.png"
    except Exception as e:
        print(f"Context Processor Error: {e}")
        context['ai_name'] = 'うたー'
        context['character'] = 'inu'
        context['character_img'] = "/static/codemon/images/characters/inu.png"
    return context
