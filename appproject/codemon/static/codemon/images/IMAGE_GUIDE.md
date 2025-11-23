# Codemon 画像配置ガイド

## ディレクトリ構造

```
codemon/static/codemon/images/
├── backgrounds/
│   └── bg_common.png          # 全画面共通の背景
├── frames/
│   ├── bg_frame_yellow.png    # karihome, 新規登録, ログイン
│   ├── bg_frame_blue.png      # システム機能
│   ├── bg_frame_purple.png    # アルゴリズム機能
│   ├── bg_frame_green.png     # チェックリスト
│   ├── bg_frame_pink.png      # グループ参加系
│   ├── bg_frame_black.png     # その他グループ系
│   └── bg_frame_white.png     # ログアウト
├── characters/
│   ├── inu.png                # キャラクター立ち絵（既存）
│   ├── usagi.png
│   ├── kitune.png
│   └── ...                    # その他キャラクター
├── karihome/
│   └── speech_bubble.png      # 吹き出し画像（必要な場合）
└── nav/
    ├── home.png / home_active.png
    ├── system.png / system_active.png
    ├── algorithm.png / algorithm_active.png
    ├── checklist.png / checklist_active.png
    └── account.png / account_active.png
```

## 画像配置手順

### 1. 背景画像
```
配置先: codemon/static/codemon/images/backgrounds/bg_common.png
説明: 全画面で共通の背景画像
推奨サイズ: 1920x1080 以上
```

### 2. 外枠画像（7色）
```
配置先: codemon/static/codemon/images/frames/
ファイル名: bg_frame_{色名}.png

- bg_frame_yellow.png  ← karihome用（最優先）
- bg_frame_blue.png
- bg_frame_purple.png
- bg_frame_green.png
- bg_frame_pink.png
- bg_frame_black.png
- bg_frame_white.png

推奨サイズ: 背景と同じサイズ
説明: 透過PNG推奨、背景の上に重ねる
```

### 3. キャラクター立ち絵
```
配置先: codemon/static/codemon/images/characters/
説明: 既存のキャラクター画像を使用
推奨サイズ: 高さ 600px 程度
形式: 透過PNG
```

### 4. 吹き出し（オプション）
```
配置先: codemon/static/codemon/images/karihome/speech_bubble.png
説明: CSSで作成可能なため、画像は任意
```

## karihome 最優先で必要な画像

最低限、以下の3つがあればkarihomeを完成できます:

1. **bg_common.png** (backgrounds/)
2. **bg_frame_yellow.png** (frames/)
3. キャラクター立ち絵（既存のものを使用）

## 画像の実際の配置方法

### Windows エクスプローラーで配置:
```
C:\Users\y_fujita\OneDrive - ooharastudent\デスクトップ\sotugyou\code\codemon\appproject\codemon\static\codemon\images\
```

### コマンドで確認:
```bash
cd "C:/Users/y_fujita/OneDrive - ooharastudent/デスクトップ/sotugyou/code/codemon/appproject/codemon/static/codemon/images"
ls -la backgrounds/ frames/ characters/ karihome/
```

## 次のステップ

画像を配置したら:
1. ブラウザで http://127.0.0.1:8000/accounts/karihome/ にアクセス
2. 画像が正しく表示されることを確認
3. 他の画面に展開

## トラブルシューティング

### 画像が表示されない場合:
```bash
# Django の静的ファイルを再収集
python manage.py collectstatic --noinput

# 開発サーバー再起動
Ctrl+C してから python manage.py runserver
```

### 画像パスの確認:
ブラウザの開発者ツール（F12）で Network タブを確認し、
404 エラーが出ていないかチェック
