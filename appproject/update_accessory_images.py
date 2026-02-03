"""
アクセサリーの画像設定を更新するスクリプト
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory


def update_accessory_images():
    """画像が存在するアクセサリーの設定を更新"""
    
    # 存在する画像ファイルのマッピング
    image_mapping = {
        # Crown系
        ('crown', 'arupaka'): 'codemon/images/accessories/crown_arupaka.png',
        ('crown', 'fukurou'): 'codemon/images/accessories/crown_fukurou.png',
        ('crown', 'inu'): 'codemon/images/accessories/crown_inu.png',
        ('crown', 'kitsune'): 'codemon/images/accessories/crown_kitune.png',  # ファイル名がkituneになっている
        ('crown', 'neko'): 'codemon/images/accessories/crown_neko.png',
        ('crown', 'risu'): 'codemon/images/accessories/crown_risu.png',
        ('crown', 'usagi'): 'codemon/images/accessories/crown_usagi.png',
        
        # Neko系の各カテゴリ
        ('flower', 'neko'): 'codemon/images/accessories/flower_neko.png',
        ('glasses', 'neko'): 'codemon/images/accessories/glasses_neko.png',
        ('hat', 'neko'): 'codemon/images/accessories/hat_neko.png',
        ('ribbon', 'neko'): 'codemon/images/accessories/ribbon_neko.png',
        ('star', 'neko'): 'codemon/images/accessories/star_neko.png',
    }
    
    updated_count = 0
    
    for (category, character), image_path in image_mapping.items():
        # CSSクラス名で検索（例: "crown.arupaka"）
        css_class = f"{category}.{character}"
        
        accessories = Accessory.objects.filter(css_class=css_class)
        
        if accessories.exists():
            for accessory in accessories:
                accessory.use_image = True
                accessory.image_path = image_path
                accessory.save()
                print(f"✅ 更新: {accessory.name} -> {image_path}")
                updated_count += 1
        else:
            print(f"⚠️  見つからない: {css_class}")
    
    print(f"\n✨ 完了: {updated_count}件のアクセサリーを更新しました")
    
    # 画像が設定されたアクセサリーの数を確認
    with_image = Accessory.objects.filter(use_image=True).count()
    without_image = Accessory.objects.filter(use_image=False).count()
    
    print(f"\n📊 統計:")
    print(f"  - 画像あり: {with_image}件")
    print(f"  - 画像なし（CSS描画）: {without_image}件")
    print(f"  - 合計: {Accessory.objects.count()}件")


if __name__ == '__main__':
    print("🖼️  アクセサリーの画像設定を更新します...\n")
    update_accessory_images()
