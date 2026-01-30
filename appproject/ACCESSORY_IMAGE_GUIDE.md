# アクセサリー画像の管理方法

## 📏 画像サイズの調整

### 方法1: CSSで調整（推奨）

[accounts/templates/includes/character_widget.html](accounts/templates/includes/character_widget.html) の276行目付近：

```css
.character-with-accessory .character-accessory.flower {
  width: 48px;  /* ← ここを変更（デフォルト24px） */
  height: 48px; /* ← ここを変更（デフォルト24px） */
  border-radius: 50%;
  top: 50px;
  right: 60px;
}
```

**おすすめサイズ:**
- 小さめ: 32px × 32px
- 標準: 48px × 48px ← 現在の設定
- 大きめ: 64px × 64px
- 特大: 80px × 80px

### 方法2: 画像ファイル自体のサイズを変更

画像編集ソフトで元の画像ファイルを以下のサイズに調整：
- 推奨: 96px × 96px（CSSで縮小表示される）
- 最小: 48px × 48px
- 最大: 128px × 128px

---

## 🖼️ 既存のアクセサリーを画像版に変更する方法

### ステップ1: 画像ファイルを準備

1. PNG形式で作成（透過背景推奨）
2. ファイル名の命名規則:
   ```
   {カテゴリ}_{キャラクター}.png
   
   例:
   - flower_inu.png （花・イヌ用）
   - flower_neko.png （花・ネコ用）
   - glasses_usagi.png （眼鏡・ウサギ用）
   - ribbon_kitsune.png （リボン・キツネ用）
   ```

3. 保存場所:
   ```
   codemon/static/codemon/images/accessories/
   ```

### ステップ2: データベースを更新

#### 方法A: 変換スクリプトを使う（簡単）

```powershell
python convert_to_image_accessory.py
```

対話式で：
1. アクセサリー一覧が表示される
2. 変更したいアクセサリーのIDを入力
3. 画像ファイル名を入力（自動提案あり）
4. 完了！

#### 方法B: Djangoシェルで手動変更

```powershell
python manage.py shell
```

```python
from codemon.models import Accessory

# 例: ID=10のアクセサリーを画像版に変更
acc = Accessory.objects.get(accessory_id=10)
acc.use_image = True
acc.image_path = 'codemon/images/accessories/flower_inu.png'
acc.save()
```

#### 方法C: 一括変更（複数同時）

```python
# 全ての「花」カテゴリーを画像版に変更
from codemon.models import Accessory

accessories = Accessory.objects.filter(category='flower', css_class__contains='inu')
for acc in accessories:
    # css_class例: 'flower.inu' → 画像: 'flower_inu.png'
    filename = acc.css_class.replace('.', '_') + '.png'
    acc.image_path = f'codemon/images/accessories/{filename}'
    acc.use_image = True
    acc.save()
    print(f'✓ {acc.name} → {filename}')
```

### ステップ3: 確認

1. ブラウザをリロード（Ctrl+Shift+R）
2. キャラクターに画像が表示されることを確認

---

## 🔄 CSS描画に戻す方法

画像ではなく元のCSS描画に戻したい場合：

```python
from codemon.models import Accessory

acc = Accessory.objects.get(accessory_id=54)
acc.use_image = False
acc.save()
```

---

## 📊 現在の状態を確認

```powershell
python -c "import os, sys, django; sys.path.append('.'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings'); django.setup(); from codemon.models import Accessory; [print(f'{"[画像]" if a.use_image else "[CSS]"} {a.name} ({a.css_class})') for a in Accessory.objects.all()]"
```

または、変換スクリプトで一覧表示：

```powershell
python convert_to_image_accessory.py
# IDを聞かれたらEnterでスキップ → 一覧だけ表示
```

---

## 💡 ヒント

### 画像が表示されない場合

1. **画像パスを確認:**
   ```python
   from codemon.models import Accessory
   acc = Accessory.objects.get(accessory_id=54)
   print(f'use_image: {acc.use_image}')
   print(f'image_path: {acc.image_path}')
   ```

2. **ファイルの存在確認:**
   ```powershell
   Test-Path "codemon\static\codemon\images\accessories\flower_neko.png"
   ```
   → `True` なら存在する

3. **ブラウザのキャッシュをクリア:**
   - Ctrl+Shift+R でハードリロード

4. **開発者ツールで確認:**
   - F12 → Network タブ
   - 画像のURLが404エラーになっていないか確認

### 位置を微調整したい場合

```css
/* ネコ用の花の位置を調整 */
.character-widget[data-character="neko"] .character-accessory.flower {
  top: 55px;    /* 上下位置 */
  right: 65px;  /* 左右位置 */
}
```

### 複数の画像を一度に追加

```powershell
# 画像を一括配置
Copy-Item "C:\path\to\images\*.png" "codemon\static\codemon\images\accessories\"

# 一括変更スクリプト実行
python convert_to_image_accessory.py
```

---

## 📝 まとめ

1. **サイズ変更**: CSSの `width` と `height` を変更（現在48px）
2. **画像追加**: `codemon/static/codemon/images/accessories/` に配置
3. **データ更新**: `convert_to_image_accessory.py` で簡単変換
4. **確認**: Ctrl+Shift+R でリロード

質問があればいつでもお聞きください！
