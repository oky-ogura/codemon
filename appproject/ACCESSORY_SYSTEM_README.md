# アクセサリーシステム実装完了

## 実装内容

### 1. データベースモデル (`codemon/models.py`)

以下のモデルを追加しました：

#### コイン・実績システム
- **UserCoin**: ユーザーのコイン残高を管理
- **Achievement**: 実績マスターデータ
- **UserAchievement**: ユーザーの取得済み実績

#### アクセサリーシステム
- **Accessory**: アクセサリーマスターデータ（種類、価格、解放条件など）
- **UserAccessory**: ユーザーの所持・装備アクセサリー

### 2. ビュー機能 (`codemon/views.py`)

- `accessory_shop`: アクセサリーショップ画面
- `purchase_accessory`: アクセサリー購入処理
- `equip_accessory`: アクセサリー装備処理
- `unequip_accessory`: アクセサリー装備解除処理

### 3. URL設定 (`codemon/urls.py`)

```python
path('accessories/', views.accessory_shop, name='accessory_shop')
path('accessories/equip/<int:accessory_id>/', views.equip_accessory, name='equip_accessory')
path('accessories/unequip/', views.unequip_accessory, name='unequip_accessory')
path('accessories/purchase/<int:accessory_id>/', views.purchase_accessory, name='purchase_accessory')
```

### 4. テンプレート

- **accessory_shop.html**: アクセサリーショップUI
  - コイン残高表示
  - カテゴリ別アクセサリー一覧
  - 購入・装備・装備解除機能

### 5. キャラクター表示への統合

#### character_widget.html
- キャラクター画像とアクセサリーの重ね描画
- 大サイズ（karihomeモード）と小サイズ（アイコン）の自動切り替え
- CSS変数による柔軟なスタイリング

#### アクセサリーCSSスタイル
```css
/* 花アクセサリー */
.flower.red { background: #ff4a4a; }
.flower.blue { background: #4a7bff; }
.flower.yellow { background: #ffd84a; }
.flower.green { background: #5cd35c; }

/* 眼鏡アクセサリー */
.glasses { color: #3a7bff; }
```

#### サイズ別表示
- **karihomeモード**: 24px（花）、48px（眼鏡）
- **小アイコンモード**: 9px（花）、16px（眼鏡）

### 6. Context Processor (`accounts/context_processors.py`)

全画面でアクセサリー情報を利用可能にするため、`global_character_data` に装備中アクセサリー情報を追加。

### 7. テストデータ

`create_accessory_testdata.py` により以下を作成：

- **アクセサリー**: 5種類（赤・青・黄・緑の花、青い眼鏡）
- **初期コイン**: 全ユーザーに1000コイン付与

## 使い方

### 1. アクセサリーショップにアクセス

karihomeの右上にある「🎀 アクセサリー」ボタンをクリック  
または直接 `http://127.0.0.1:8000/codemon/accessories/` にアクセス

### 2. アクセサリーを購入

- コイン残高を確認
- 購入したいアクセサリーの「〇〇コインで購入」ボタンをクリック
- 購入後、自動的に所持品に追加されます

### 3. アクセサリーを装備

- 所持しているアクセサリーの「装備する」ボタンをクリック
- 同時に装備できるのは1個まで
- 装備すると全画面のキャラクターに表示されます

### 4. アクセサリーを外す

- 「現在の装備」セクションの「外す」ボタンをクリック

## 技術仕様

### サイズ判定ロジック

```python
# character_widget.html内で自動判定
.karihome-mode .character-accessory  # 大サイズ用
.mini-icon-wrapper .mini-accessory   # 小アイコン用
```

### 同時装備制限

```python
# views.py の equip_accessory
UserAccessory.objects.filter(user=user, is_equipped=True).update(is_equipped=False)
```

トランザクションで既存の装備を外してから新しいアクセサリーを装備。

### アクセサリーの表示位置調整

CSSの `top`, `right`, `left` プロパティで位置を微調整可能：

```css
.character-accessory.flower {
    top: 50px;      /* キャラクターからの距離 */
    right: 60px;    /* 右からの距離 */
}
```

## 今後の拡張案

1. **追加アクセサリー種類**
   - 帽子（hat）
   - リボン
   - ネックレス

2. **実績システムの本格実装**
   - 特定条件でアクセサリー解放
   - 実績達成時の通知

3. **アニメーション効果**
   - アクセサリー装備時のキラキラエフェクト
   - ホバー時のアクセサリーアニメーション

4. **コイン獲得システム**
   - タスク完了でコイン付与
   - ログインボーナス

5. **複数同時装備**
   - カテゴリ別に装備可能（花1個＋眼鏡1個など）

## ファイル一覧

### 新規作成
- `codemon/templates/codemon/accessory_shop.html`
- `create_accessory_testdata.py`
- `codemon/migrations/0002_achievement_usercoin_accessory_useraccessory_and_more.py`

### 変更
- `codemon/models.py` - モデル追加
- `codemon/views.py` - ビュー関数追加
- `codemon/urls.py` - URL設定追加
- `codemon/templates/includes/character_widget.html` - アクセサリー表示機能追加
- `accounts/views.py` - karihomeビューにアクセサリー情報追加
- `accounts/context_processors.py` - グローバルコンテキストにアクセサリー追加
- `accounts/templates/accounts/karihome.html` - アクセサリーショップボタン追加

## 動作確認

1. サーバー起動: `python manage.py runserver`
2. ログイン後、karihomeにアクセス
3. 「🎀 アクセサリー」ボタンをクリック
4. アクセサリーを購入・装備
5. karihomeに戻ってキャラクターにアクセサリーが表示されることを確認

## 完了！

アクセサリーシステムの基本実装が完了しました。
CSS変数とシンプルなDOM構造により、今後の拡張も容易です。
