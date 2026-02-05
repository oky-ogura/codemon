# アクセサリー画像の使用方法

## 概要
アクセサリーシステムで実際の画像ファイルを使用する方法です。

## 準備したもの
- ✅ Accessoryモデルに `image_path` と `use_image` フィールドを追加
- ✅ マイグレーションファイル作成済み（0003_accessory_image_fields.py）
- ✅ テンプレートで画像/CSS描画を自動切り替え
- ✅ 画像保存用ディレクトリ作成済み

## 手順

### 1. マイグレーションを実行

```powershell
cd C:\Users\h-tabuchi\Desktop\sotugyouseisaku\codemon\appproject
python manage.py migrate
```

### 2. 画像ファイルを配置

画像を以下のディレクトリに配置してください：
```
codemon/static/codemon/images/accessories/
```

**画像の推奨仕様：**
- サイズ: 24px × 24px（または48px × 48px）
- 形式: PNG（透過背景推奨）
- ファイル名例: `test_flower_inu.png`, `flower_inu.png`, `glasses_kitsune.png`

### 3. テスト用アクセサリーを作成

```powershell
python create_image_accessory_test.py
```

これで「テスト画像・イヌ」というアクセサリーが登録されます。

### 4. 画像アクセサリーを装備

```powershell
# アクセサリーIDを指定して装備（デフォルトはadminユーザー）
python test_equip_image_accessory.py 54

# 特定のユーザーに装備
python test_equip_image_accessory.py 54 20
```

### 5. ブラウザで確認

karihomeページをリロードして、キャラクターに画像が表示されているか確認してください。

## 既存のアクセサリーを画像版に変更する方法

### 方法1: Djangoシェルで変更

```powershell
python manage.py shell
```

```python
from codemon.models import Accessory

# 例: 「サンフラワー・ドッグ」を画像版に変更
acc = Accessory.objects.get(name='サンフラワー・ドッグ')
acc.image_path = 'codemon/images/accessories/flower_inu.png'
acc.use_image = True
acc.save()
print(f'✓ {acc.name} を画像版に変更しました')
```

### 方法2: 一括変更スクリプト

```python
# すべての「flower.inu」を画像版に変更
Accessory.objects.filter(css_class='flower.inu').update(
    image_path='codemon/images/accessories/flower_inu.png',
    use_image=True
)
```

## 動作の仕組み

### テンプレート（character_widget.html）

```django
{% if equipped_accessory %}
  {% if equipped_accessory.accessory.use_image and equipped_accessory.accessory.image_path %}
    {# 画像を使用 #}
    <span class="character-accessory acc use-image {{ css_class }}" 
          style="background-image: url('{% static image_path %}');"></span>
  {% else %}
    {# CSS描画（従来） #}
    <span class="character-accessory acc {{ css_class }}"></span>
  {% endif %}
{% endif %}
```

### CSS

```css
/* 画像アクセサリー用の共通スタイル */
.character-accessory.use-image {
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  border-radius: 0; /* 画像の形をそのまま使う */
}

/* CSS描画（従来）*/
.flower.inu { background: #FFD700; }
```

## トラブルシューティング

### 画像が表示されない場合

1. **画像パスを確認**
   ```python
   from codemon.models import Accessory
   acc = Accessory.objects.get(name='テスト画像・イヌ')
   print(acc.image_path)  # 'codemon/images/accessories/test_flower_inu.png'
   print(acc.use_image)   # True
   ```

2. **静的ファイルの配置を確認**
   ```powershell
   Test-Path "codemon\static\codemon\images\accessories\test_flower_inu.png"
   ```
   → True が返ってくればOK

3. **ブラウザの開発者ツールで確認**
   - F12キーで開発者ツールを開く
   - Networkタブで画像のリクエストを確認
   - 404エラーが出ていないか確認

4. **静的ファイルを再収集（本番環境の場合）**
   ```powershell
   python manage.py collectstatic
   ```

### CSS描画に戻したい場合

```python
acc = Accessory.objects.get(name='テスト画像・イヌ')
acc.use_image = False
acc.save()
```

## ファイル命名規則（推奨）

画像ファイル名は以下の形式を推奨：
- `{category}_{character}.png`
- 例: `flower_inu.png`, `glasses_kitsune.png`, `hat_usagi.png`

これにより、css_classと対応させやすくなります：
- css_class: `flower.inu` → 画像: `flower_inu.png`
- css_class: `glasses.kitsune` → 画像: `glasses_kitsune.png`
