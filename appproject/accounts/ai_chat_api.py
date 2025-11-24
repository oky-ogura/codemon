from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from codemon.services import chat_gemini
from .models import AiConfig
from .views import get_logged_account

@csrf_exempt
def ai_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = request.POST or request.body
        if hasattr(data, 'get'):
            message = data.get('message', '')
        else:
            import json
            data = json.loads(data)
            message = data.get('message', '')
        acc = get_logged_account(request)
        ai_config = None
        character = 'inu'
        if acc:
            ai_config = AiConfig.objects.filter(user_id=acc.user_id).first()
            if ai_config and ai_config.appearance:
                character = ai_config.appearance.lower().replace('.png', '')
        # Gemini APIでAI返答を生成
        # Gemini APIは履歴必須。履歴なしで空リストを渡す
        ai_reply = chat_gemini(message, [], character)
        return JsonResponse({'reply': ai_reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
