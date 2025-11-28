"""
Gemini API接続テストスクリプト
"""
import os
import sys

# Django設定を読み込む
import django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.conf import settings
import google.generativeai as genai

def test_api():
    print("=== Gemini API 接続テスト ===\n")
    
    # APIキーを取得
    api_key = getattr(settings, 'AI_API_KEY', '') or os.getenv('AI_API_KEY', '')
    if not api_key:
        print("❌ エラー: APIキーが設定されていません")
        return False
    
    print(f"✓ APIキー: {api_key[:20]}..." if len(api_key) > 20 else f"✓ APIキー: {api_key}")
    
    # モデル名を取得
    model_name = getattr(settings, 'AI_MODEL', '') or os.getenv('AI_MODEL', 'gemini-2.0-flash')
    print(f"✓ モデル: {model_name}\n")
    
    try:
        # APIを設定
        genai.configure(api_key=api_key)
        
        # テストメッセージを送信
        print("APIにテストメッセージを送信中...")
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 100,
        }
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )
        
        response = model.generate_content("こんにちは")
        
        if response and response.text:
            print(f"✅ 成功! AIからの応答:\n{response.text}\n")
            return True
        else:
            print("❌ エラー: 応答が空です")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}\n")
        
        # よくあるエラーの説明
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
            print("💡 このエラーは以下の原因が考えられます:")
            print("   - APIの無料枠を使い切った")
            print("   - 1分間のリクエスト制限を超えた (無料版は15リクエスト/分)")
            print("   - 同じAPIキーを複数人で使用している")
        elif "invalid" in error_str or "api key" in error_str:
            print("💡 このエラーは以下の原因が考えられます:")
            print("   - APIキーが無効または期限切れ")
            print("   - APIキーの入力ミス")
        elif "permission" in error_str:
            print("💡 このエラーは以下の原因が考えられます:")
            print("   - このAPIキーには指定されたモデルへのアクセス権限がない")
            print("   - Gemini APIが有効化されていない")
        
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
