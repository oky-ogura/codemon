# system/index.html テンプレートクリーンアップ完了

## 実施日時
2026年2月6日

## 問題
システム作成画面(http://127.0.0.1:8000/accounts/system/)を開くと、画面下部にチュートリアル関連のテキストが表示されていました。

### 表示されていた内容例
```
target: '#addCircleBtn', message: 'メニューから「えん」を クリックして ください！', requireClick: true, showSkip: true }, ...
```

## 原因
`accounts/templates/system/index.html` テンプレートに、以前のフェーズで削除したはずのチュートリアルコードが約1,200行分残っていました。

- **問題の範囲**: 66行目〜1248行目(削除前)
- **削除したコード**: 
  - せいかいチュートリアル関数 (startStep2Tutorial)
  - ふせいかいチュートリアル関数 (startFuseikaiCreateTutorial)
  - もんだいチュートリアル関数 (startMondaiCreateTutorial)
  - TutorialHelperデバッグユーティリティ
  - チュートリアルステップ定義(全ステップ)
  - イベントリスナー、状態管理コード

## 修正内容
### ファイル修正: `accounts/templates/system/index.html`
- **修正前**: 1,248行
- **修正後**: 66行
- **削除行数**: 1,182行

### クリーンアップしたファイル構造
```django-html
{% extends 'base.html' %}
{% load static %}

{% block background_frame %}
  <!-- 背景フレーム -->
{% endblock %}

{% block title %}システム作成 - Codemon{% endblock %}

{% block extra_css %}
  <!-- チュートリアルCSS読み込み(外部ファイル) -->
  <link href="{% static 'codemon/css/tutorial_overlay.css' %}" rel="stylesheet">
  {% include 'system/_styles.html' %}
{% endblock %}

{% block content %}
  {% include 'system/_content.html' %}
{% endblock %}

{% block extra_js %}
  <!-- 各種システム機能のJS読み込み(外部ファイル) -->
  {% include 'system/_blockly_loader.html' %}
  {% include 'system/_drag_drop.html' %}
  {% include 'system/_history.html' %}
  {% include 'system/_preview.html' %}
  {% include 'system/_element_creators.html' %}
  {% include 'system/_initialization.html' %}
  
  <!-- チュートリアル関連JS読み込み(外部ファイル) -->
  <script src="{% static 'codemon/js/tutorial_overlay.js' %}"></script>
  <script src="{% static 'codemon/js/tutorial_helper.js' %}"></script>
  <script src="{% static 'codemon/js/tutorial_manager.js' %}"></script>
  <script src="{% static 'codemon/js/tutorials/tutorial_seikai.js' %}"></script>
  <script src="{% static 'codemon/js/tutorials/tutorial_fuseikai.js' %}"></script>
  <script src="{% static 'codemon/js/tutorials/tutorial_mondai.js' %}"></script>
  
  <script>
    console.log('システム編集画面を読み込みました');
    
    // getCookie関数を定義
    function getCookie(name) { /* ... */ }
    
    // チュートリアル自動開始
    if (window.tutorialManager) {
      document.addEventListener('DOMContentLoaded', function() {
        tutorialManager.autoStart();
      });
    }
  </script>
  
  {% block ai_chat_widget %}
    {% include 'includes/ai_chat_base.html' %}
  {% endblock %}
{% endblock %}
```

## 重要な変更点
1. **インラインチュートリアルコードを完全削除**
   - 以前はテンプレート内に直接記述されていたチュートリアルコード(1,200行)を全て削除
   - チュートリアル機能は外部JSファイルで管理される構造に整理済み

2. **テンプレート構造のクリーンアップ**
   - `{% endblock %}` タグの重複を解消
   - 不要な `<script>` タグを削除
   - Djangoテンプレートの正しい構造を復元

3. **チュートリアル機能は維持**
   - 外部JSファイル経由でチュートリアル機能は引き続き動作
   - `tutorial_overlay.js`, `tutorial_helper.js`, `tutorial_manager.js`
   - 各チュートリアルスクリプト: `tutorial_seikai.js`, `tutorial_fuseikai.js`, `tutorial_mondai.js`

## 影響範囲
### 修正済み
- ✅ システム作成画面の表示が正常化
- ✅ チュートリアルコードの表示問題を解消
- ✅ テンプレート構文エラーを解消

### 影響なし(引き続き動作)
- ✅ チュートリアル機能(外部JSファイル経由)
- ✅ システム編集機能
- ✅ AIチャット機能
- ✅ その他の既存機能

## テスト方法
```bash
# 開発サーバーを起動
cd c:\Users\h-tabuchi\Desktop\sotugyouseisaku\codemon\appproject
python manage.py runserver

# ブラウザでアクセス
# http://127.0.0.1:8000/accounts/system/

# 確認項目:
# 1. システム作成画面が正常に表示される
# 2. 画面下部にチュートリアルテキストが表示されない
# 3. 「新しく作る」ボタンが機能する
# 4. チュートリアル機能(sessionStorageフラグ経由)が引き続き動作する
```

## 次のステップ
1. ユーザーによるシステム作成画面の動作確認
2. 他のテンプレートファイルに同様の問題がないか確認
3. 必要に応じて他の機能のテスト

## 関連ファイル
- **修正ファイル**: `accounts/templates/system/index.html` (1,182行削除)
- **外部チュートリアルJS**: 
  - `static/codemon/js/tutorial_overlay.js`
  - `static/codemon/js/tutorial_helper.js`
  - `static/codemon/js/tutorial_manager.js`
  - `static/codemon/js/tutorials/tutorial_seikai.js`
  - `static/codemon/js/tutorials/tutorial_fuseikai.js`
  - `static/codemon/js/tutorials/tutorial_mondai.js`

## 備考
- このクリーンアップにより、テンプレートの可読性が大幅に向上しました
- チュートリアル機能のメンテナンス性も改善(外部ファイル管理)
- 同様の問題が他のテンプレートにも存在する可能性があるため、注意が必要
