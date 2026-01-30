"""
アクセサリーのCSS classのスペースをドットに修正するスクリプト
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory

def fix_css_classes():
    """CSS classのスペースをドットに修正"""
    accessories = Accessory.objects.all()
    
    print("修正前のCSS class:")
    for acc in accessories:
        print(f"  {acc.name}: [{acc.css_class}]")
    
    print("\n修正中...")
    updated_count = 0
    
    for acc in accessories:
        # スペースをドットに置換
        if ' ' in acc.css_class:
            old_class = acc.css_class
            acc.css_class = acc.css_class.replace(' ', '.')
            acc.save()
            print(f"  ✓ {acc.name}: [{old_class}] → [{acc.css_class}]")
            updated_count += 1
    
    print(f"\n✅ 完了！ {updated_count}件のアクセサリーを修正しました。")
    
    print("\n修正後のCSS class:")
    accessories = Accessory.objects.all()
    for acc in accessories:
        print(f"  {acc.name}: [{acc.css_class}]")

if __name__ == '__main__':
    fix_css_classes()
