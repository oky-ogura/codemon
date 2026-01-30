from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Account
from codemon.models import UserCoin

@receiver(post_save, sender=Account)
def create_user_coin(sender, instance, created, **kwargs):
    """ユーザー作成時に自動的にコインを付与"""
    if created:
        UserCoin.objects.get_or_create(
            user=instance,
            defaults={'balance': 10000, 'total_earned': 10000}
        )
        print(f"✓ {instance.user_name} に10000コイン付与しました")