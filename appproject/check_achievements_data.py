import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Achievement, UserStats
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== 実績データ確認 ===")
achs = Achievement.objects.all().order_by('category', 'target_count')
print(f"総実績数: {achs.count()}")
print()

for category in ['system', 'algorithm', 'login', 'consecutive_login', 'ai_chat']:
    cat_achs = achs.filter(category=category)
    print(f"[{category}]: {cat_achs.count()}件")
    for a in cat_achs:
        print(f"  - {a.name} (target={a.target_count}, tier={a.tier})")
    print()

print("=== ユーザー統計 ===")
user = User.objects.first()
if user:
    stats, _ = UserStats.objects.get_or_create(user=user)
    print(f"ユーザー: {user.username}")
    print(f"システム作成数: {stats.total_systems}")
    print(f"アルゴリズム作成数: {stats.total_algorithms}")
    print(f"ログイン日数: {stats.total_login_days}")
    print(f"連続ログイン: {stats.consecutive_login_days}")
    print(f"AI会話回数: {stats.total_ai_chats}")
