# フェーズ2実装ガイド

## 📋 概要

フェーズ2では、チュートリアルコードを独立したJavaScriptファイルに抽出し、HTMLファイルをシンプルにします。

## ✅ 完了した作業

### 1. tutorial_manager.js（統括マネージャー）

**ファイル:** [codemon/static/codemon/js/tutorial_manager.js](codemon/static/codemon/js/tutorial_manager.js)

**主要機能:**
- フラグチェーン管理（11個のフラグ）
- チュートリアル登録・自動開始システム
- 進行状況追跡（0-100%）
- 現在のフェーズ検出
- デバッグ用ツール

**使用例:**
```javascript
// フラグの状態確認
tutorialManager.showStatus()

// 特定のフェーズにジャンプ（デバッグ用）
jumpToPhase('fuseikai')  // ふせいかいフェーズへ
location.reload()

// チュートリアル登録
tutorialManager.register('seikai', {
    trigger: {
        requireFlag: tutorialManager.FLAGS.START,
        forbidFlag: tutorialManager.FLAGS.SEIKAI_SAVE
    },
    steps: () => { /* ステップ定義 */ },
    onComplete: () => { /* 完了処理 */ }
});

// 自動開始（ページロード時）
tutorialManager.autoStart();
```

### 2. tutorial_seikai.js（せいかいチュートリアル）

**ファイル:** [codemon/static/codemon/js/tutorials/tutorial_seikai.js](codemon/static/codemon/js/tutorials/tutorial_seikai.js)

**改善点:**
- 即時関数で名前空間汚染を防止
- `tutorialHelper`を使用した非破壊的イベント監視
- MutationObserverで効率的な要素待機
- TutorialManagerに自動登録

**ステップ構成:**
1. イントロダクション
2. 実行ボタン説明
3. 保存ボタン説明
4. 図形ボタンクリック
5. 円の追加
6. 円の右クリック待機
7. 色と大きさ変更
8. フォームボタンクリック
9. テキストボックス追加
10. テキストボックス配置
11. テキスト入力（「せいかい！」）
12. 保存指示

## 🚧 残りの作業

### 3. 他のチュートリアルファイル作成

以下のファイルを作成する必要があります：

#### tutorial_fuseikai.js
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_fuseikai.js`
- **ステップ数:** 9ステップ
- **トリガー:** `FUSEIKAI_CREATE`フラグ
- **完了フラグ:** `FUSEIKAI_SAVE`

#### tutorial_mondai.js  
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_mondai.js`
- **ステップ数:** 12ステップ
- **トリガー:** `MONDAI_CREATE`フラグ
- **完了フラグ:** `MONDAI_CREATED`

#### tutorial_algorithm.js
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_algorithm.js`
- **ステップ数:** 11ステップ
- **トリガー:** `MONDAI_CREATED`フラグ
- **完了フラグ:** `ALGORITHM_SAVED`
- **特記事項:** block/index.htmlで使用

#### tutorial_list.js（一覧画面用）
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_list.js`
- **内容:**
  - せいかい一覧チュートリアル（3ステップ）
  - ふせいかい一覧チュートリアル（3ステップ）
- **トリガー:** `SEIKAI_SAVED`, `FUSEIKAI_SAVED`フラグ
- **特記事項:** system_list.htmlで使用

#### tutorial_test.js
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_test.js`
- **ステップ数:** 7ステップ
- **トリガー:** `ALGORITHM_SAVED`フラグ
- **完了フラグ:** `COMPLETED`

#### tutorial_save.js（保存画面用）
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_save.js`
- **内容:**
  - せいかい保存完了チュートリアル
  - ふせいかい保存完了チュートリアル
- **トリガー:** `SEIKAI_SAVE`, `FUSEIKAI_SAVE`フラグ

#### tutorial_create.js（名前入力画面用）
- **場所:** `codemon/static/codemon/js/tutorials/tutorial_create.js`
- **内容:**
  - せいかい名前入力チュートリアル
  - ふせいかい名前入力チュートリアル
- **トリガー:** `SEIKAI_SAVE`, `FUSEIKAI_SAVE`フラグ

### 4. HTMLファイルの簡素化

各HTMLファイルから大量のチュートリアルコードを削除し、シンプルなscriptタグに置き換えます。

#### Before（現在）:
```html
<script>
function startStep2Tutorial() {
  // 500行以上のチュートリアルコード...
}

// チュートリアル起動処理
(function() {
  if (sessionStorage.getItem('tutorial_step2_start') === 'true') {
    // 初期化コード...
    startStep2Tutorial();
  }
})();
</script>
```

#### After（目標）:
```html
<!-- チュートリアル関連スクリプト -->
<script src="{% static 'codemon/js/tutorial_helper.js' %}"></script>
<script src="{% static 'codemon/js/tutorial_manager.js' %}"></script>
<script src="{% static 'codemon/js/tutorials/tutorial_seikai.js' %}"></script>
<script src="{% static 'codemon/js/tutorials/tutorial_fuseikai.js' %}"></script>
<script src="{% static 'codemon/js/tutorials/tutorial_mondai.js' %}"></script>

<script>
// チュートリアル自動開始
document.addEventListener('DOMContentLoaded', () => {
    if (window.tutorialManager) {
        tutorialManager.autoStart();
    }
});
</script>
```

**削減行数の見込み:**
- system/index.html: -900行
- system/system_list.html: -500行
- system/save.html: -200行
- system/system_create.html: -300行
- block/index.html: -200行
- **合計: -2100行以上**

## 🎯 実装の優先順位

### 優先度1（すぐ実装）
1. ✅ tutorial_manager.js
2. ✅ tutorial_seikai.js
3. ⏸️ tutorial_fuseikai.js
4. ⏸️ tutorial_mondai.js

### 優先度2（次に実装）
5. ⏸️ tutorial_algorithm.js
6. ⏸️ tutorial_test.js

### 優先度3（最後に実装）
7. ⏸️ tutorial_list.js
8. ⏸️ tutorial_save.js
9. ⏸️ tutorial_create.js

### 優先度4（統合作業）
10. ⏸️ 各HTMLファイルの簡素化
11. ⏸️ 動作確認
12. ⏸️ ドキュメント作成

## 📝 テンプレート（新規チュートリアルファイル作成用）

```javascript
/**
 * tutorial_xxx.js - XXXチュートリアル
 */

(function() {
    'use strict';
    
    function getXxxSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'XXXチュートリアルを開始します',
                nextText: 'つぎへ'
            },
            // ... 他のステップ
        ];
    }
    
    if (window.tutorialManager) {
        tutorialManager.register('xxx', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.XXX_FLAG,
                forbidFlag: tutorialManager.FLAGS.YYY_FLAG
            },
            steps: getXxxSteps,
            onComplete: function() {
                console.log('🎉 XXXチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.NEXT_FLAG);
            },
            onSkip: function() {
                if (confirm('チュートリアルをスキップしますか？')) {
                    tutorialManager.setFlag(tutorialManager.FLAGS.NEXT_FLAG);
                    return true;
                }
                return false;
            }
        });
        
        console.log('📝 XXXチュートリアル登録完了');
    }
})();
```

## 🔧 デバッグコマンド

フェーズ2実装中に使えるコマンド：

```javascript
// 現在の状態確認
tutorialManager.showStatus()

// 登録済みチュートリアル一覧
tutorialManager.listTutorials()

// フェーズジャンプ
jumpToPhase('seikai')      // せいかいから開始
jumpToPhase('fuseikai')    // ふせいかいから開始
jumpToPhase('mondai')      // もんだいから開始
jumpToPhase('algorithm')   // アルゴリズムから開始
jumpToPhase('test')        // テストから開始

// フラグ操作
tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVE)
tutorialManager.removeFlag(tutorialManager.FLAGS.SEIKAI_SAVE)
tutorialManager.clearAllFlags()

// 強制開始
tutorialManager.forceStart('seikai')
```

## 📊 期待される効果

### コード品質
- **行数削減:** -2100行以上（HTMLファイル）
- **可読性:** 各チュートリアルが独立したファイルで管理
- **保守性:** 修正が1ファイルで完結

### 開発効率
- **テスト容易性:** 個別にチュートリアルをテスト可能
- **並行開発:** 複数のチュートリアルを同時に開発可能
- **再利用性:** チュートリアルシステムを他のページでも使用可能

### パフォーマンス
- **初期ロード:** HTMLファイルサイズ削減
- **キャッシュ:** JavaScriptファイルがブラウザキャッシュに保存
- **メンテナンス:** 不要なチュートリアルコードを簡単に削除

## 🚀 次のステップ

1. **残りのチュートリアルファイル作成**
   - テンプレートを使って効率的に作成
   - 既存HTMLからコードをコピー＆調整

2. **HTMLファイルの簡素化**
   - scriptタグを追加
   - 既存のチュートリアルコードを削除

3. **動作確認**
   - 各フェーズのチュートリアルが正常に動作するか確認
   - フラグチェーンが正しく機能するか確認

4. **ドキュメント作成**
   - フェーズ2完了レポート作成
   - 開発者向けガイド更新

フェーズ1で基礎を固め、フェーズ2でコードを整理。これにより、チュートリアルシステムが持続可能な構造になります！
