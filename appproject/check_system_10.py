import os
import django

# Djangoの設定をロード
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import System
from accounts.models import Account

# システムID 10を検索
try:
    system = System.objects.get(system_id=10)
    print(f"✅ システムID 10が見つかりました:")
    print(f"  - システム名: {system.system_name}")
    print(f"  - ユーザーID: {system.user.user_id}")
    print(f"  - ユーザー名: {system.user.name}")
except System.DoesNotExist:
    print("❌ システムID 10は存在しません")
    
# すべてのシステムを表示
print("\n=== すべてのシステム ===")
systems = System.objects.all()
for sys in systems:
    print(f"ID: {sys.system_id}, 名前: {sys.system_name}, ユーザー: {sys.user.name}")
