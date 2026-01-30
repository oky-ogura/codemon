"""
画像アクセサリーを装備するテストスクリプト
使用方法: python test_equip_image_accessory.py <accessory_id>
"""
import os
import sys
import django

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from django.db import transaction
from codemon.models import Accessory, UserAccessory
from accounts.models import Account

def equip_image_accessory(user_id, accessory_id):
    """指定したユーザーに画像アクセサリーを装備"""
    try:
        with transaction.atomic():
            # ユーザーとアクセサリーを取得
            user = Account.objects.get(user_id=user_id)
            accessory = Accessory.objects.get(accessory_id=accessory_id)
            
            print(f'ユーザー: {user.user_name} (ID: {user_id})')
            print(f'アクセサリー: {accessory.name}')
            print(f'  - CSSクラス: {accessory.css_class}')
            print(f'  - 画像パス: {accessory.image_path}')
            print(f'  - 画像を使用: {accessory.use_image}')
            
            # まず所持していなければ追加
            user_acc, created = UserAccessory.objects.get_or_create(
                user=user,
                accessory=accessory
            )
            
            if created:
                print('\n✓ アクセサリーを所持リストに追加しました')
            else:
                print('\n✓ すでに所持しています')
            
            # 他のアクセサリーの装備を外す
            UserAccessory.objects.filter(user=user, is_equipped=True).update(is_equipped=False)
            
            # このアクセサリーを装備
            user_acc.is_equipped = True
            user_acc.save()
            
            print(f'✓ {accessory.name} を装備しました！')
            
            # 確認
            equipped = UserAccessory.objects.filter(user=user, is_equipped=True).first()
            if equipped:
                print(f'\n現在装備中: {equipped.accessory.name}')
                print(f'  - use_image: {equipped.accessory.use_image}')
                if equipped.accessory.use_image:
                    print(f'  - 画像が表示されるはずです: /static/{equipped.accessory.image_path}')
                else:
                    print(f'  - CSS描画が表示されます')
            
            return True
            
    except Account.DoesNotExist:
        print(f'エラー: ユーザーID {user_id} が見つかりません')
        return False
    except Accessory.DoesNotExist:
        print(f'エラー: アクセサリーID {accessory_id} が見つかりません')
        return False
    except Exception as e:
        print(f'エラー: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('使用方法: python test_equip_image_accessory.py <accessory_id> [user_id]')
        print('例: python test_equip_image_accessory.py 54')
        print('    python test_equip_image_accessory.py 54 20  # 特定のユーザーに装備')
        sys.exit(1)
    
    accessory_id = int(sys.argv[1])
    user_id = int(sys.argv[2]) if len(sys.argv) > 2 else 20  # デフォルトはadmin
    
    print('=== 画像アクセサリー装備テスト ===\n')
    success = equip_image_accessory(user_id, accessory_id)
    
    if success:
        print('\n【確認方法】')
        print('1. ブラウザでkarihomeページを開く（またはリロード）')
        print('2. キャラクターに画像が表示されているか確認')
        print('3. 表示されない場合:')
        print('   - ブラウザの開発者ツール(F12)でコンソールエラーを確認')
        print('   - 画像パスが正しいか確認')
        print('   - 静的ファイルが配置されているか確認')
