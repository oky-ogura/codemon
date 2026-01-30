"""
画像を使用するアクセサリーのテスト登録スクリプト
実験として1つだけ画像アクセサリーを登録します
"""
import os
import sys
import django

# Djangoプロジェクトのパスを設定
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory

def create_image_accessory():
    """画像を使用するアクセサリーを1つ作成（テスト用）"""
    
    # テスト用の画像アクセサリー（ネコ用の花）
    test_accessory, created = Accessory.objects.update_or_create(
        name='フラワー・ネコ（画像版）',
        defaults={
            'category': 'flower',
            'css_class': 'flower.neko',  # ドット記法
            'image_path': 'codemon/images/accessories/flower_neko.png',  # 画像パス
            'use_image': True,  # 画像を使用
            'description': '画像を使用したネコ用の花アクセサリー',
            'unlock_coins': 0,  # テスト用に無料
        }
    )
    
    if created:
        print(f'✓ 画像アクセサリーを新規作成しました: {test_accessory.name}')
        print(f'  - ID: {test_accessory.accessory_id}')
        print(f'  - CSSクラス: {test_accessory.css_class}')
        print(f'  - 画像パス: {test_accessory.image_path}')
        print(f'  - use_image: {test_accessory.use_image}')
    else:
        print(f'✓ 既存のアクセサリーを更新しました: {test_accessory.name}')
        print(f'  - ID: {test_accessory.accessory_id}')
    
    return test_accessory

if __name__ == '__main__':
    print('=== 画像アクセサリーのテスト登録 ===\n')
    accessory = create_image_accessory()
    
    print('\n【次のステップ】')
    print('1. 画像ファイルを以下のパスに配置してください:')
    print(f'   codemon/static/{accessory.image_path}')
    print('\n2. 画像の推奨仕様:')
    print('   - サイズ: 24px × 24px （または48px × 48px）')
    print('   - 形式: PNG（透過背景推奨）')
    print('   - 背景: 透明（alpha channel）')
    print('\n3. テスト方法:')
    print('   - データベースに登録したので、ショップから購入・装備できます')
    print('   - または以下のコマンドで直接装備:')
    print(f'   python test_equip_image_accessory.py {accessory.accessory_id}')
