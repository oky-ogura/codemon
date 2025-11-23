# Codemon デザイン展開ガイド

## 完成したもの

✅ **karihome** - 基本デザイン完成
- 背景画像システム
- 外枠色切り替え
- キャラクター・吹き出しレイアウト
- キーボード操作対応
- 楽しいインタラクション

---

## 他画面への展開パターン

### パターン1: 同じレイアウト（キャラ+吹き出し型）

`system_choice.html`, `block_choice.html` など

```django-html
{% extends 'base.html' %}
{% load static %}

{% block title %}システム選択 - Codemon{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'codemon/css/redesign.css' %}">
{% endblock %}

{% block content %}
<!-- 共通背景 -->
<img src="{% static 'codemon/images/backgrounds/bg_common.png' %}" 
     alt="" class="bg-common">

<!-- 外枠（システム用=青） -->
<img src="{% static 'codemon/images/frames/bg_frame_blue.png' %}" 
     alt="" class="bg-frame frame-blue">

<div class="main-content">
  <!-- 吹き出し内にコンテンツ -->
  <div class="speech-bubble-container">
    <div class="speech-bubble">
      <h2 class="text-fun">どのシステムで学ぶ?</h2>
      
      <!-- ここに既存の機能（ボタンやリストなど）を配置 -->
      {% block inner_content %}{% endblock %}
    </div>
  </div>

  <!-- キャラクター -->
  <div class="character-container">
    <img src="{% static 'codemon/images/characters' %}/{{ request.session.ai_character|default:'inu' }}.png" 
         alt="AIキャラクター" class="character-image">
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'codemon/js/interactions.js' %}"></script>
{% endblock %}
```

### パターン2: コンテンツ中心型（リスト表示画面）

`system_list.html`, `algorithm_list.html` など

```django-html
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'codemon/css/redesign.css' %}">
<style>
  .content-area {
    max-width: 1200px;
    margin: 40px auto;
    padding: 30px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
</style>
{% endblock %}

{% block content %}
<!-- 共通背景 + 外枠 -->
<img src="{% static 'codemon/images/backgrounds/bg_common.png' %}" 
     alt="" class="bg-common">
<img src="{% static 'codemon/images/frames/bg_frame_blue.png' %}" 
     alt="" class="bg-frame frame-blue">

<div class="main-content">
  <div class="content-area">
    <!-- 既存のリストやテーブルをここに -->
    {% block inner_content %}{% endblock %}
  </div>
  
  <!-- 小さめのキャラクター（オプション） -->
  <div class="character-container" style="right: 50px; max-width: 250px;">
    <img src="{% static 'codemon/images/characters' %}/{{ request.session.ai_character|default:'inu' }}.png" 
         alt="AIキャラクター" class="character-image">
  </div>
</div>
{% endblock %}
```

### パターン3: フォーム画面

`account_entry.html`, `login.html` など

```django-html
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'codemon/css/redesign.css' %}">
<style>
  .form-container {
    max-width: 600px;
    margin: 60px auto;
    padding: 40px;
    background: white;
    border-radius: 25px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  }
</style>
{% endblock %}

{% block content %}
<img src="{% static 'codemon/images/backgrounds/bg_common.png' %}" 
     alt="" class="bg-common">
<img src="{% static 'codemon/images/frames/bg_frame_yellow.png' %}" 
     alt="" class="bg-frame frame-yellow">

<div class="main-content center-content">
  <div class="form-container">
    <h2 class="text-fun" style="text-align: center; margin-bottom: 30px;">
      アカウント情報
    </h2>
    
    <form method="post" class="form-custom">
      {% csrf_token %}
      <!-- 既存のフォームフィールド -->
      {{ form.as_p }}
      
      <button type="submit" class="btn-custom">
        <!-- ボタン画像をここに -->
        送信
      </button>
    </form>
  </div>
</div>
{% endblock %}
```

---

## 外枠色の使い分け

既存の画面に適用する際の外枠色マッピング:

| 画面グループ | 外枠色 | クラス名 |
|------------|--------|---------|
| karihome, 新規登録, ログイン | 黄色 | `frame-yellow` |
| system_choice, system_list など | 青 | `frame-blue` |
| block_choice, algorithm_list など | 紫 | `frame-purple` |
| checklist_* | 緑 | `frame-green` |
| group参加系 | ピンク | `frame-pink` |
| その他group系 | 黒 | `frame-black` |
| logout | 白 | `frame-white` |

---

## 既存画面の改変手順

### ステップ1: テンプレートを開く
```bash
codemon/templates/accounts/system_choice.html  # 例
```

### ステップ2: 既存コンテンツを保持しながら追加

```django-html
{# 既存のコード #}
{% extends 'base.html' %}

{# 追加: static読み込み #}
{% load static %}

{% block title %}システム選択 - Codemon{% endblock %}

{# 追加: CSS #}
{% block extra_css %}
<link rel="stylesheet" href="{% static 'codemon/css/redesign.css' %}">
{% endblock %}

{% block content %}
{# 追加: 背景と外枠 #}
<img src="{% static 'codemon/images/backgrounds/bg_common.png' %}" alt="" class="bg-common">
<img src="{% static 'codemon/images/frames/bg_frame_blue.png' %}" alt="" class="bg-frame frame-blue">

{# 既存のコンテンツをdivで囲む #}
<div class="main-content">
  {# ここに既存のHTML #}
</div>
{% endblock %}

{# 追加: JS #}
{% block extra_js %}
<script src="{% static 'codemon/js/interactions.js' %}"></script>
{% endblock %}
```

---

## 作業の優先順位

1. ✅ **karihome** (完了)
2. 🔄 **system_choice** (同じレイアウトで簡単)
3. 🔄 **block_choice** (system_choiceとほぼ同じ)
4. 🔄 その他の画面

---

## コンフリクト回避のコツ

### 方法1: ブランチ分離
```bash
git checkout -b feature/redesign-system
# system関連を変更
git commit -m "Add: system画面デザイン適用"
```

### 方法2: 段階的コミット
```bash
# 小さく分けてコミット
git add accounts/templates/accounts/system_choice.html
git commit -m "Add: system_choice背景画像追加"

git add codemon/static/codemon/images/frames/bg_frame_blue.png
git commit -m "Add: システム用外枠画像"
```

### 方法3: 同じファイルを触らない
- HTMLテンプレート: あなたが担当
- views.py, models.py: 他メンバー
→ コンフリクトしにくい

---

## トラブルシューティング

### レイアウトが崩れる場合
```css
/* base.htmlのcontent-wrapperを上書き */
.content-wrapper {
  background: transparent !important;
  padding: 0 !important;
  max-width: none !important;
}
```

### 画像が表示されない
```bash
python manage.py collectstatic --noinput
```

---

次に作業する画面を教えてください!
