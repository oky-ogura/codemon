"""
既存のアクセサリーを画像版に変更するスクリプト

使用方法:
1. 画像ファイルを codemon/static/codemon/images/accessories/ に配置
   例: flower_inu.png, glasses_kitsune.png

2. このスクリプトを実行して、アクセサリーIDを指定
   python convert_to_image_accessory.py

3. または、アクセサリー名で検索して変更
"""
import os
import sys
import django

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory

def list_accessories():
    """全アクセサリーを一覧表示"""
    accessories = Accessory.objects.all().order_by('accessory_id')
    print('\n=== アクセサリー一覧 ===')
    for acc in accessories:
        status = '📷 画像' if acc.use_image else '🎨 CSS'
        image_info = f' → {acc.image_path}' if acc.use_image else ''
        print(f'{status} ID:{acc.accessory_id:3d} | {acc.name:30s} | CSS: {acc.css_class}{image_info}')
    return accessories

def convert_to_image(accessory_id, image_filename):
    """指定したアクセサリーを画像版に変更"""
    try:
        acc = Accessory.objects.get(accessory_id=accessory_id)
        
        # 画像パスを設定（codemon/images/accessories/からの相対パス）
        image_path = f'codemon/images/accessories/{image_filename}'
        
        print(f'\n=== 変更内容 ===')
        print(f'アクセサリー: {acc.name}')
        print(f'CSS クラス: {acc.css_class}')
        print(f'変更前: {"画像使用" if acc.use_image else "CSS描画"}')
        if acc.use_image:
            print(f'  画像: {acc.image_path}')
        
        # 更新
        acc.use_image = True
        acc.image_path = image_path
        acc.save()
        
        print(f'変更後: 画像使用')
        print(f'  画像: {image_path}')
        print(f'\n✓ 変更完了！')
        
        # 画像ファイルの存在確認
        full_path = os.path.join('codemon', 'static', image_path)
        if os.path.exists(full_path):
            print(f'✓ 画像ファイル確認: {full_path}')
        else:
            print(f'⚠ 警告: 画像ファイルが見つかりません: {full_path}')
            print(f'  画像を配置してください。')
        
        return True
        
    except Accessory.DoesNotExist:
        print(f'エラー: アクセサリーID {accessory_id} が見つかりません')
        return False
    except Exception as e:
        print(f'エラー: {e}')
        return False

def search_and_convert(search_term):
    """名前またはCSS classで検索して変更"""
    results = Accessory.objects.filter(
        models.Q(name__icontains=search_term) | 
        models.Q(css_class__icontains=search_term)
    )
    
    if not results:
        print(f'"{search_term}" に一致するアクセサリーが見つかりません')
        return
    
    print(f'\n=== "{search_term}" の検索結果 ===')
    for acc in results:
        status = '📷 画像' if acc.use_image else '🎨 CSS'
        print(f'{status} ID:{acc.accessory_id} | {acc.name} | {acc.css_class}')

if __name__ == '__main__':
    print('╔═══════════════════════════════════════════════════════╗')
    print('║     アクセサリー画像変換ツール                        ║')
    print('╚═══════════════════════════════════════════════════════╝')
    
    # 一覧表示
    accessories = list_accessories()
    
    print('\n' + '='*60)
    print('【使い方】')
    print('1. 一覧からIDを確認')
    print('2. 画像ファイルを配置: codemon/static/codemon/images/accessories/')
    print('3. IDと画像ファイル名を入力')
    print('='*60)
    
    # 対話式で変更
    try:
        acc_id = input('\nアクセサリーID (Enter でスキップ): ').strip()
        if acc_id:
            acc_id = int(acc_id)
            
            # 画像ファイル名を提案
            acc = Accessory.objects.get(accessory_id=acc_id)
            # css_class から画像ファイル名を生成（例: flower.inu → flower_inu.png）
            suggested_name = acc.css_class.replace('.', '_') + '.png'
            
            print(f'\n推奨ファイル名: {suggested_name}')
            image_file = input(f'画像ファイル名 [{suggested_name}]: ').strip()
            if not image_file:
                image_file = suggested_name
            
            convert_to_image(acc_id, image_file)
            
            print('\n【次のステップ】')
            print('1. ブラウザをリロード（Ctrl+Shift+R）')
            print('2. 画像が表示されることを確認')
            
    except ValueError:
        print('無効な入力です')
    except KeyboardInterrupt:
        print('\n\n中断しました')
