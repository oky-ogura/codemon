"""
ネコ用アクセサリーを画像版に一括変換するスクリプト
"""
import os
import sys
import django

# Djangoセットアップ
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory

def main():
    # 変換対象: (アクセサリーID, 画像ファイル名)
    updates = [
        (9, 'flower_neko.png'),     # クールブルーム・キャット
        (17, 'glasses_neko.png'),   # マイペースグラス・キャット
        (25, 'ribbon_neko.png'),    # きまぐれリボン・キャット
        (33, 'star_neko.png'),      # ナイトスター・キャット
        (41, 'hat_neko.png'),       # フリーダムハット・キャット
        (49, 'crown_neko.png'),     # クールクラウン・キャット
    ]
    
    print('=== ネコ用アクセサリーを画像版に変換中 ===\n')
    
    success_count = 0
    for accessory_id, image_file in updates:
        try:
            acc = Accessory.objects.get(accessory_id=accessory_id)
            acc.image_path = f'codemon/images/accessories/{image_file}'
            acc.use_image = True
            acc.save()
            print(f'✓ ID:{accessory_id:2d} | {acc.name:35s} → {image_file}')
            success_count += 1
        except Accessory.DoesNotExist:
            print(f'✗ ID:{accessory_id:2d} | アクセサリーが見つかりません')
        except Exception as e:
            print(f'✗ ID:{accessory_id:2d} | エラー: {e}')
    
    print(f'\n合計 {success_count}/{len(updates)} 個のアクセサリーを画像版に変換しました')
    
    # 結果確認
    print('\n=== 更新結果の確認 ===')
    neko_accessories = Accessory.objects.filter(
        css_class__endswith='.neko'
    ).order_by('category', 'accessory_id')
    
    for acc in neko_accessories:
        status = '📷 画像' if acc.use_image else '🎨 CSS'
        print(f'{status} | ID:{acc.accessory_id:2d} | {acc.category:8s} | {acc.name:35s}')
        if acc.use_image:
            print(f'       └─ {acc.image_path}')

if __name__ == '__main__':
    main()
