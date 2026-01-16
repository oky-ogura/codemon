from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from codemon.services import chat_gemini
from .models import AiConfig
from .views import get_logged_account
import json

@csrf_exempt
def ai_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = request.POST or request.body
        if hasattr(data, 'get'):
            message = data.get('message', '')
        else:
            data = json.loads(data)
            message = data.get('message', '')
        acc = get_logged_account(request)
        ai_config = None
        character = 'inu'
        if acc:
            ai_config = AiConfig.objects.filter(user_id=acc.user_id).first()
            if ai_config and ai_config.appearance:
                character = ai_config.appearance.lower().replace('.png', '')
        
        # セッションから会話履歴を取得（キャラクターごとに保持）
        session_key = f'ai_chat_history_{character}'
        history_raw = request.session.get(session_key, [])
        # セッションはリストで保存されるのでタプルに変換
        history_pairs = [(h[0], h[1]) for h in history_raw if len(h) >= 2]
        
        # デバッグログ
        print(f"[DEBUG] Session key: {session_key}")
        print(f"[DEBUG] History pairs count: {len(history_pairs)}")
        for i, (role, content) in enumerate(history_pairs):
            print(f"[DEBUG] History[{i}]: {role} = {content[:50]}...")
        
        # Gemini APIでAI返答を生成（履歴を渡す）
        ai_reply = chat_gemini(message, history_pairs, character)
        
        # エラーレスポンスの場合は履歴に追加しない
        if ai_reply.startswith('[') and ']' in ai_reply:
            return JsonResponse({'reply': ai_reply})
        
        # 履歴を更新（最大10往復まで保持）
        history_raw.append(['user', message])
        history_raw.append(['assistant', ai_reply])
        if len(history_raw) > 20:  # 10往復 = 20メッセージ
            history_raw = history_raw[-20:]
        request.session[session_key] = history_raw
        
        return JsonResponse({'reply': ai_reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
