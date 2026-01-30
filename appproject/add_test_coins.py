import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from accounts.models import Account
from codemon.models import UserCoin

def add_coins_to_all_users(amount=10000):
    """全ユーザーに指定されたコイン数を追加"""
    accounts = Account.objects.all()
    
    if not accounts.exists():
        print("ユーザーが見つかりません。")
        return
    
    for account in accounts:
        # UserCoinレコードを取得または作成
        user_coin, created = UserCoin.objects.get_or_create(
            user=account,
            defaults={'balance': 0, 'total_earned': 0}
        )
        
        old_balance = user_coin.balance
        user_coin.balance += amount
        user_coin.total_earned += amount
        user_coin.save()
        
        print(f"ユーザー: {account.user_name} - {old_balance}コイン → {user_coin.balance}コイン (+{amount})")
    
    print(f"\n✓ {accounts.count()}人のユーザーに{amount}コインを追加しました。")

def set_coins_for_all_users(amount=10000):
    """全ユーザーのコイン数を指定された値に設定"""
    accounts = Account.objects.all()
    
    if not accounts.exists():
        print("ユーザーが見つかりません。")
        return
    
    for account in accounts:
        # UserCoinレコードを取得または作成
        user_coin, created = UserCoin.objects.get_or_create(
            user=account,
            defaults={'balance': amount, 'total_earned': amount}
        )
        
        old_balance = user_coin.balance
        user_coin.balance = amount
        user_coin.save()
        
        print(f"ユーザー: {account.user_name} - {old_balance}コイン → {user_coin.balance}コイン")
    
    print(f"\n✓ {accounts.count()}人のユーザーのコインを{amount}に設定しました。")

if __name__ == '__main__':
    print("=== テスト用コイン追加スクリプト ===\n")
    
    # どちらか選択してください：
    
    # 方法1: 現在のコインに10000コインを追加
    add_coins_to_all_users(10000)
    
    # 方法2: コイン数を10000に設定（コメントを外して使用）
    # set_coins_for_all_users(10000)
    
    print("\n完了しました！")
