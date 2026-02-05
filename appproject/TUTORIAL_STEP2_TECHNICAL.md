# STEP2チュートリアル 技術仕様書（Copilot用）

## 🤖 このドキュメントについて

このドキュメントは、GitHub Copilot（AI）がSTEP2チュートリアルの実装を引き継ぐために必要な技術情報を網羅的にまとめたものです。

**重要な前提知識**:
- このプロジェクトは小学生向けプログラミング学習アプリ「Codemon」
- Djangoバックエンド + vanilla JavaScript フロントエンド
- sessionStorageによる状態管理
- Blocklyによるビジュアルプログラミング

---

## 📁 ディレクトリ構造

```
appproject/
├── accounts/
│   ├── templates/
│   │   ├── accounts/
│   │   │   └── karihome.html          # ホーム画面（STEP1, STEP2完了）
│   │   └── system/
│   │       ├── index.html              # システム作成・編集画面（STEP2メイン）
│   │       ├── system_choice.html      # システム選択画面
│   │       ├── system_create.html      # システム保存確認画面
│   │       ├── system_list.html        # システム一覧画面
│   │       ├── _history.html           # 履歴管理（保存ボタン）
│   │       ├── _preview.html           # プレビュー（要素収集）
│   │       ├── _initialization.html    # 初期化（要素復元）
│   │       ├── _element_creators.html  # 要素作成関数
│   │       ├── _styles.html            # スタイル定義
│   │       ├── _drag_drop.html         # ドラッグ&ドロップ
│   │       └── _blockly_loader.html    # Blockly読み込み
│   └── views.py                        # バックエンドビュー
├── codemon/
│   └── static/
│       └── codemon/
│           ├── js/
│           │   └── tutorial_overlay.js # TutorialOverlayクラス
│           └── css/
│               └── tutorial_overlay.css # チュートリアルスタイル
└── appproject/
    └── settings.py                     # Django設定
```

---

## 🔧 技術スタック

### フロントエンド
- **Vanilla JavaScript** (ES6+)
- **sessionStorage** (状態管理)
- **Blockly** (ビジュアルプログラミング)
- **CSS3** (アニメーション、グリッドレイアウト)

### バックエンド
- **Django 5.2.6**
- **PostgreSQL**
- **Python 3.12.3**

### チュートリアルシステム
- **TutorialOverlay class** (独自実装)
- **4分割オーバーレイ** (上下左右の暗幕)
- **動的ハイライト** (操作対象の強調)

---

## 🎯 チュートリアルフロー（完全版）

### フェーズ1: せいかい画面作成（✅ 実装済み）

```
[system_choice.html]
  ユーザー: 「新しく作る」ボタンクリック
  システム: sessionStorage.setItem('tutorial_step2_start', 'true')
  遷移: system/index.html
    ↓
[system/index.html - DOMContentLoaded]
  検出: sessionStorage.getItem('tutorial_step2_start') === 'true'
  実行: startStep2Tutorial()
  削除: sessionStorage.removeItem('tutorial_step2_start')
    ↓
[チュートリアルステップ 1-13]
  1. ウェルカムメッセージ（画面中央）
  2. 実行ボタン説明（#executeBtn）
  3. 保存ボタン説明（#saveBtn）
  4. せいかい画面作成開始（画面中央）
  5. 図形ボタンクリック（#shapeBtn） → 自動で図形メニュー開く
  6. 円ボタンクリック（#addCircleBtn） → 円要素追加検出
  7. 円の右クリック指示（.main-area） → 編集パネル開閉検出
  8. 色・大きさ変更（.shape-settings-panel） → 適用ボタンクリック検出
  9. フォームボタンクリック（#formBtn） → 自動でフォームメニュー開く
  10. テキストボックスボタンクリック（#addTextBoxBtn）
  11. テキストボックス配置（.main-area） → 要素追加検出
  12. テキスト入力（.text-box-container） → 「せいかい!」検出
  13. 保存ボタンクリック（#saveBtn）
  設定: sessionStorage.setItem('tutorial_step2_seikai_save', 'true')
  遷移: system_create.html
    ↓
[system_create.html - DOMContentLoaded]
  検出: sessionStorage.getItem('tutorial_step2_seikai_save') === 'true'
  実行: startSaveSystemTutorial()
  削除: sessionStorage.removeItem('tutorial_step2_seikai_save')
    ↓
[チュートリアルステップ 1-2]
  1. システム名入力（#systemName） → 「せいかい」検出
  2. 保存ボタンクリック（#saveBtn）
  設定: sessionStorage.setItem('tutorial_step2_fuseikai_create', 'true')
  遷移: system_list.html
```

### フェーズ2: ふせいかい画面作成（❌ 未実装）

```
[system_list.html]
  ユーザー: 「新しく作る」ボタンクリック
  遷移: system/index.html
    ↓
[system/index.html - DOMContentLoaded]
  検出: sessionStorage.getItem('tutorial_step2_fuseikai_create') === 'true'
  実行: startFuseikaiCreateTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_fuseikai_create')
    ↓
[チュートリアルステップ 1-10]（❌ 未実装）
  1. ふせいかい画面作成開始（画面中央）
  2. 図形ボタンクリック（#shapeBtn）
  3. 三角ボタンクリック（#addTriangleBtn） → 三角要素追加検出
  4. 三角の右クリック指示（.main-area） → 編集パネル開閉検出
  5. 色・大きさ変更（.shape-settings-panel） → RGB(0,0,255)、150px
  6. フォームボタンクリック（#formBtn）
  7. テキストボックスボタンクリック（#addTextBoxBtn）
  8. テキストボックス配置（.main-area）
  9. テキスト入力（.text-box-container） → 「ふせいかい!」検出
  10. 保存ボタンクリック（#saveBtn）
  設定: sessionStorage.setItem('tutorial_step2_fuseikai_save', 'true')
  遷移: system_create.html
    ↓
[system_create.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_fuseikai_save') === 'true'
  実行: startSaveFuseikaiTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_fuseikai_save')
    ↓
[チュートリアルステップ 1-2]（❌ 未実装）
  1. システム名入力（#systemName） → 「ふせいかい」検出
  2. 保存ボタンクリック（#saveBtn）
  設定: sessionStorage.setItem('tutorial_step2_mondai_create', 'true')
  遷移: system_list.html
```

### フェーズ3: もんだい画面作成（❌ 未実装）

```
[system_list.html]
  ユーザー: 「新しく作る」ボタンクリック
  遷移: system/index.html
    ↓
[system/index.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_mondai_create') === 'true'
  実行: startMondaiCreateTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_mondai_create')
    ↓
[チュートリアルステップ 1-13]（❌ 未実装）
  1. もんだい画面作成開始（画面中央）
  2. フォームボタンクリック（#formBtn）
  3. チェックボックスボタンクリック（#addCheckboxBtn）
  4. ラベル入力（チェックボックス設定パネル） → 「1+1は?」検出
  5. 項目数確認（デフォルト3のまま）
  6. 作成ボタンクリック → チェックボックス要素追加検出
  7. 項目1編集 → 「1」検出
  8. 項目2編集 → 「2」検出
  9. 項目3編集 → 「3」検出
  10. ボタン機能クリック（#buttonBtn）
  11. ボタン作成（そのまま作成）
  12. ボタン右クリック → コンテキストメニュー検出
  13. アルゴリズム新規作成クリック
  設定: sessionStorage.setItem('tutorial_step2_algorithm_create', 'true')
  遷移: block.html
```

### フェーズ4: アルゴリズム作成（❌ 未実装）

```
[block.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_algorithm_create') === 'true'
  実行: startAlgorithmCreateTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_algorithm_create')
    ↓
[チュートリアルステップ 1-15]（❌ 未実装）
  1. アルゴリズム作成開始（画面中央）
  2. システム機能タブクリック
  3. 「もしシステム〇〇の～」ブロッククリック → ワークスペース配置検出
  4. リスト1選択（「仮保存_日時」） → 選択変更検出
  5. リスト2選択（「1+1は?」） → 選択変更検出
  6. リスト3選択（「項目:2」） → 選択変更検出
  7. システムタブクリック
  8. 「システムを表示」ブロッククリック → ワークスペース配置検出
  9. リスト選択（「せいかい」） → 選択変更検出
  10. ブロックドラッグ → 「すること」穴への接続検出
  11. ブロック右クリック → コンテキストメニュー検出
  12. ブロックコピー → ブロック複製検出
  13. リスト選択変更（「ふせいかい」） → 選択変更検出
  14. ブロックドラッグ → 「そうでなければ」穴への接続検出
  15. 保存ボタンクリック
  設定: sessionStorage.setItem('tutorial_step2_algorithm_save', 'true')
  遷移: アルゴリズム保存画面（ダイアログまたは別ページ）
    ↓
[アルゴリズム保存画面]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_algorithm_save') === 'true'
  実行: startAlgorithmSaveTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_algorithm_save')
    ↓
[チュートリアルステップ 1-4]（❌ 未実装）
  1. アルゴリズム名入力 → 「チュートリアル」検出
  2. 詳細入力 → 「チュートリアルぶんき」検出
  3. 保存するボタンクリック
  4. ダイアログOKクリック → 「システム編集画面に戻りますか?」
  設定: sessionStorage.setItem('tutorial_step2_test_execute', 'true')
  遷移: system/index.html（もんだい画面）
```

### フェーズ5: テスト実行・保存（❌ 未実装）

```
[system/index.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_test_execute') === 'true'
  実行: startTestExecuteTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_test_execute')
    ↓
[チュートリアルステップ 1-12]（❌ 未実装）
  1. テスト実行開始（画面中央）
  2. 実行ボタンクリック（#executeBtn）
  3. チェックボックス2にチェック → チェック状態検出
  4. ボタンクリック → せいかい画面遷移検出
  5. せいかい画面確認（画面中央）
  6. 閉じるボタンクリック → もんだい画面復帰検出
  7. 実行ボタンクリック（2回目）
  8. チェックボックス3にチェック → チェック状態検出
  9. ボタンクリック → ふせいかい画面遷移検出
  10. ふせいかい画面確認（画面中央）
  11. 閉じるボタンクリック → もんだい画面復帰検出
  12. 保存ボタンクリック
  設定: sessionStorage.setItem('tutorial_step2_mondai_save', 'true')
  遷移: system_create.html
    ↓
[system_create.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_mondai_save') === 'true'
  実行: startSaveMondaiTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_mondai_save')
    ↓
[チュートリアルステップ 1-4]（❌ 未実装）
  1. システム名入力 → 「もんだい」検出
  2. 詳細入力 → 「チュートリアルもんだい」検出
  3. 保存するボタンクリック
  4. メイン画面へボタンクリック
  設定: sessionStorage.setItem('tutorial_step2_complete', 'true')
  遷移: karihome.html
    ↓
[karihome.html - DOMContentLoaded]（❌ 未実装）
  検出: sessionStorage.getItem('tutorial_step2_complete') === 'true'
  実行: startStep2CompleteTutorial()（❌ 未実装）
  削除: sessionStorage.removeItem('tutorial_step2_complete')
    ↓
[チュートリアルステップ 1]（❌ 未実装）
  1. STEP2完了メッセージ（画面中央）
  POST: /accounts/complete-tutorial-step/ {step: 2}
  終了: チュートリアル完了
```

---

## 🔑 重要な技術実装詳細

### TutorialOverlay クラス

#### ファイル: `codemon/static/codemon/js/tutorial_overlay.js`

#### クラス構造

```javascript
class TutorialOverlay {
  constructor() {
    this.currentStep = 0;
    this.steps = [];
    this.onComplete = null;
    this.onSkip = null;
    this.overlayParts = null;        // 4つのオーバーレイ矩形
    this.highlight = null;            // ハイライト枠
    this.messageBox = null;           // メッセージボックス
    this.currentTargetElement = null; // 現在のターゲット要素
    this.currentTargetOriginalStyles = null; // 元のスタイル保存
  }
}
```

#### 主要メソッド

**init(steps, options)**
```javascript
tutorialOverlay.init(steps, {
  onComplete: function() {
    console.log('✅ チュートリアル完了');
  },
  onSkip: function() {
    // スキップ処理
    return true; // スキップを許可
  }
});
```

**showStep(stepIndex)**
```javascript
showStep(stepIndex) {
  // 1. ステップ範囲チェック → complete()
  // 2. ステップ情報取得
  // 3. target判定:
  //    - null or centerMessage=true → showFullOverlay() + showCenterMessage()
  //    - 要素あり → positionHighlight() + positionOverlayParts() + showMessage()
  // 4. onShowコールバック実行
  // 5. makeTargetClickable() (requireClick=true時)
}
```

**positionHighlight(element)**
```javascript
positionHighlight(element) {
  const rect = element.getBoundingClientRect();
  const padding = 10;
  
  this.highlight.style.top = `${rect.top - padding}px`;
  this.highlight.style.left = `${rect.left - padding}px`;
  this.highlight.style.width = `${rect.width + padding * 2}px`;
  this.highlight.style.height = `${rect.height + padding * 2}px`;
  this.highlight.style.display = 'block';
}
```

**positionOverlayParts(element)**
```javascript
positionOverlayParts(element) {
  const rect = element.getBoundingClientRect();
  const padding = 10;
  
  const highlightTop = rect.top - padding;
  const highlightLeft = rect.left - padding;
  const highlightRight = rect.right + padding;
  const highlightBottom = rect.bottom + padding;
  
  // overlayParts[0]: 上部（0 → highlightTop）
  // overlayParts[1]: 下部（highlightBottom → 100%）
  // overlayParts[2]: 左部（highlightTop → highlightBottom, 0 → highlightLeft）
  // overlayParts[3]: 右部（highlightTop → highlightBottom, highlightRight → 100%）
}
```

**showMessage(step, targetElement)**
```javascript
showMessage(step, targetElement) {
  // 1. メッセージHTML生成（ステップ表示、内容、ボタン）
  // 2. カスタム位置指定チェック（messagePosition）
  //    - 'left': 左寄せ（20px）
  //    - 'right': 要素の右側
  //    - 未指定: 自動（下→上の順で配置可能判定）
  // 3. 位置計算（getBoundingClientRect + viewport調整）
  // 4. 矢印クラス追加（arrow-top, arrow-bottom）
}
```

**makeTargetClickable(element, step)**
```javascript
makeTargetClickable(element, step) {
  // 1. 元のスタイル保存（zIndex, position, pointerEvents）
  // 2. z-index = 10002（オーバーレイより上）
  // 3. requireClick時: クリックリスナー追加
  //    - クリック検出 → 元のスタイル復元 → onNext or next()
  // 4. requireClick無し: currentTargetElement保存（next()で復元）
}
```

**next()**
```javascript
next() {
  // 1. 前のターゲット要素のスタイル復元
  // 2. showStep(this.currentStep + 1)
}
```

**complete() / skip() / close()**
```javascript
complete() {
  if (this.onComplete) this.onComplete();
  this.close();
}

skip() {
  if (confirm('チュートリアルをとばしますか？')) {
    if (this.onSkip) this.onSkip();
    this.close();
  }
}

close() {
  // オーバーレイ、ハイライト、メッセージボックスをフェードアウト後削除
}
```

#### ステップオブジェクト完全仕様

```javascript
{
  // ターゲット指定
  target: '#elementId' | '.className' | null,
  
  // 表示モード
  centerMessage: false,  // true: 強制画面中央、targetを無視
  
  // メッセージ
  message: 'HTMLメッセージ<br>改行可能',
  
  // 位置調整
  messagePosition: 'left' | 'right' | undefined,  // カスタム位置指定
  
  // ボタン制御
  nextText: 'つぎへ' | null,    // 次へボタンのテキスト（nullで非表示）
  showNextButton: true | false, // 次へボタン表示フラグ
  showSkip: true | false,       // スキップボタン表示フラグ
  
  // 操作待機
  requireClick: false,  // true: ターゲット要素のクリック待機
  
  // コールバック
  onShow: function() {
    // ステップ表示時に実行
    // ここで検出ロジック、イベントリスナー追加などを行う
  },
  
  onNext: function() {
    // 次へ進む前に実行
    // 自動でnext()を呼ぶか、手動で呼ぶかを制御
  }
}
```

### 操作検出パターン

#### パターン1: クリック検出（requireClick）

```javascript
{
  target: '#addCircleBtn',
  message: 'メニューから「えん」を クリックして ください！',
  requireClick: true,
  onNext: function() {
    // クリック後の処理
    setTimeout(() => tutorialOverlay.next(), 300);
  }
}
```

**処理フロー**:
1. showStep() → makeTargetClickable()
2. 要素にクリックイベントリスナー追加
3. クリック検出 → onNext実行 → 自動またはonNext内でnext()

#### パターン2: 要素追加検出（setInterval）

```javascript
{
  target: '#addCircleBtn',
  requireClick: true,
  onNext: function() {
    // 円が配置されるのを待つ
    let checkCount = 0;
    const maxChecks = 20;
    
    const waitForCircle = setInterval(() => {
      checkCount++;
      const circles = document.querySelectorAll('[data-shape-type="circle"]');
      
      if (circles.length > 0 || checkCount >= maxChecks) {
        clearInterval(waitForCircle);
        
        if (circles.length > 0) {
          const lastCircle = circles[circles.length - 1];
          window.tutorialState.createdCircle = lastCircle;
          setTimeout(() => tutorialOverlay.next(), 500);
        } else {
          console.warn('⚠️ 円が見つかりませんでした');
          tutorialOverlay.next();
        }
      }
    }, 100);
  }
}
```

**処理フロー**:
1. ボタンクリック → onNext実行
2. setInterval開始（100ms間隔）
3. 要素チェック（最大2秒）
4. 要素発見 → clearInterval → 保存 → next()

**重要**: 必ずclearInterval()を呼び、メモリリークを防ぐ

#### パターン3: パネル開閉検出

```javascript
{
  target: '.main-area',
  onShow: function() {
    const checkForPanel = setInterval(() => {
      const panel = document.querySelector('.shape-settings-panel');
      if (panel) {
        clearInterval(checkForPanel);
        setTimeout(() => tutorialOverlay.next(), 300);
      }
    }, 100);
  }
}
```

**処理フロー**:
1. showStep() → onShow実行
2. setInterval開始
3. パネル要素チェック
4. パネル発見 → clearInterval → next()

#### パターン4: テキスト入力検出

```javascript
{
  target: '.text-box-container',
  onShow: function() {
    const checkTextInput = setInterval(() => {
      const textAreas = document.querySelectorAll('.text-box');
      let textCorrect = false;
      
      textAreas.forEach(textArea => {
        const value = textArea.value.trim();
        if (value.includes('せいかい！') || 
            value.includes('せいかい!') || 
            value.includes('せいかい')) {
          textCorrect = true;
        }
      });
      
      if (textCorrect) {
        clearInterval(checkTextInput);
        setTimeout(() => tutorialOverlay.next(), 500);
      }
    }, 100);
  }
}
```

**処理フロー**:
1. onShow実行 → setInterval開始
2. 全テキストエリアをチェック
3. 条件一致 → clearInterval → next()

**ポイント**: 複数の表記パターンに対応（全角・半角、感嘆符の違い）

#### パターン5: ボタンクリック検出（一時的リスナー）

```javascript
{
  target: '.shape-settings-panel',
  onShow: function() {
    const checkApplyButton = setInterval(() => {
      const applyBtn = document.getElementById('shapeApplyBtn');
      
      if (applyBtn && !applyBtn.dataset.tutorialListenerAdded) {
        applyBtn.dataset.tutorialListenerAdded = 'true';
        
        const applyClickHandler = function(e) {
          clearInterval(checkApplyButton);
          setTimeout(() => tutorialOverlay.next(), 500);
          applyBtn.removeEventListener('click', applyClickHandler);
          delete applyBtn.dataset.tutorialListenerAdded;
        };
        
        applyBtn.addEventListener('click', applyClickHandler);
      }
    }, 100);
  }
}
```

**処理フロー**:
1. パネル表示後、適用ボタンを検索
2. ボタン発見 → イベントリスナー追加
3. `dataset.tutorialListenerAdded`で重複登録防止
4. クリック検出 → clearInterval → next()
5. イベントリスナー削除 → フラグ削除

**重要**: イベントリスナーの重複登録を防ぎ、必ず削除する

### sessionStorage管理

#### フラグ命名規則

```
tutorial_step2_[action]
```

- `start`: チュートリアル開始
- `seikai_save`: せいかい保存画面
- `fuseikai_create`: ふせいかい作成開始
- `fuseikai_save`: ふせいかい保存画面
- `mondai_create`: もんだい作成開始
- `algorithm_create`: アルゴリズム作成開始
- `algorithm_save`: アルゴリズム保存画面
- `test_execute`: テスト実行開始
- `mondai_save`: もんだい保存画面
- `complete`: STEP2完了

#### フラグ設定・削除パターン

```javascript
// 設定（遷移前）
sessionStorage.setItem('tutorial_step2_seikai_save', 'true');
console.log('📝 tutorial_step2_seikai_save フラグを設定しました');

// 検出（遷移後）
const shouldStart = sessionStorage.getItem('tutorial_step2_seikai_save');
console.log('🔍 tutorial_step2_seikai_save チェック:', shouldStart);

if (shouldStart === 'true') {
  // 削除（起動直後）
  sessionStorage.removeItem('tutorial_step2_seikai_save');
  
  // チュートリアル開始
  startSaveSystemTutorial();
}
```

#### システムデータの保存

```javascript
// 保存ボタンクリック時（_history.html）
const elementsData = collectCurrentElements();
sessionStorage.setItem('systemDesignContent', JSON.stringify(elementsData));
sessionStorage.setItem('navigatingToCreate', 'true');

// システム作成確認画面（system_create.html）
const savedContent = sessionStorage.getItem('systemDesignContent');
const elementsDataInput = document.getElementById('elementsData');
if (savedContent && elementsDataInput) {
  elementsDataInput.value = savedContent;
}

// やめるボタン（system_create.html）
sessionStorage.setItem('returnFromCreate', 'true');
window.location.href = '/accounts/system/';

// 初期化（_initialization.html）
const returnFromCreate = sessionStorage.getItem('returnFromCreate');
const savedContent = sessionStorage.getItem('systemDesignContent');
if (returnFromCreate === 'true' && savedContent) {
  const elementsData = JSON.parse(savedContent);
  restoreSystemElements(elementsData);
  sessionStorage.removeItem('returnFromCreate');
  sessionStorage.removeItem('systemDesignContent');
}
```

### 要素の収集と復元

#### collectCurrentElements() - _preview.html

```javascript
window.collectCurrentElements = function collectCurrentElements() {
  const slideArea = document.getElementById('slideArea');
  if (!slideArea) return [];
  
  const elements = [];
  const slide = slideArea.querySelector('.slide');
  if (!slide) return [];
  
  // テキスト入力
  slide.querySelectorAll('.input-container').forEach(container => {
    const input = container.querySelector('input[type="text"]');
    const isNumber = input.hasAttribute('data-number-input');
    elements.push({
      element_type: isNumber ? 'number_input' : 'text_input',
      position_x: parseInt(container.style.left) || 0,
      position_y: parseInt(container.style.top) || 0,
      width: parseInt(container.style.width),
      height: parseInt(container.style.height),
      element_value: input.value,
      element_config: {
        placeholder: input.placeholder
      }
    });
  });
  
  // 日時入力
  slide.querySelectorAll('.input-container input[type="datetime-local"]').forEach(input => {
    const container = input.closest('.input-container');
    elements.push({
      element_type: 'datetime_input',
      position_x: parseInt(container.style.left) || 0,
      position_y: parseInt(container.style.top) || 0,
      width: parseInt(container.style.width),
      height: parseInt(container.style.height),
      element_value: input.value
    });
  });
  
  // チェックボックスグループ
  slide.querySelectorAll('.checkbox-group').forEach(group => {
    const label = group.querySelector('.group-label')?.textContent || '';
    const checkboxes = Array.from(group.querySelectorAll('.checkbox-item')).map(item => ({
      label: item.querySelector('.checkbox-label')?.textContent || '',
      value: item.querySelector('input[type="checkbox"]')?.value || ''
    }));
    elements.push({
      element_type: 'checkbox_group',
      position_x: parseInt(group.style.left) || 0,
      position_y: parseInt(group.style.top) || 0,
      width: parseInt(group.style.width),
      height: parseInt(group.style.height),
      element_value: label,
      element_config: {
        options: checkboxes
      }
    });
  });
  
  // ラジオボタングループ
  slide.querySelectorAll('.radio-group').forEach(group => {
    const label = group.querySelector('.group-label')?.textContent || '';
    const radios = Array.from(group.querySelectorAll('.radio-item')).map(item => ({
      label: item.querySelector('.radio-label')?.textContent || '',
      value: item.querySelector('input[type="radio"]')?.value || ''
    }));
    elements.push({
      element_type: 'radio_group',
      position_x: parseInt(group.style.left) || 0,
      position_y: parseInt(group.style.top) || 0,
      width: parseInt(group.style.width),
      height: parseInt(group.style.height),
      element_value: label,
      element_config: {
        options: radios
      }
    });
  });
  
  // ボタン
  slide.querySelectorAll('.draggable-btn').forEach(btn => {
    elements.push({
      element_type: 'button',
      position_x: parseInt(btn.style.left) || 0,
      position_y: parseInt(btn.style.top) || 0,
      width: parseInt(btn.style.width),
      height: parseInt(btn.style.height),
      element_value: btn.textContent
    });
  });
  
  // テキストボックス
  slide.querySelectorAll('.text-box-container').forEach(container => {
    const textInput = container.querySelector('.text-box');
    elements.push({
      element_type: 'text_box',
      position_x: parseInt(container.style.left) || 0,
      position_y: parseInt(container.style.top) || 0,
      width: parseInt(container.style.width),
      height: parseInt(container.style.height),
      element_value: textInput.value,
      element_config: {
        fontSize: parseInt(textInput.style.fontSize) || 16,
        color: textInput.style.color || '#000000'
      }
    });
  });
  
  // ルーレット
  slide.querySelectorAll('.roulette-container').forEach(container => {
    const items = Array.from(container.querySelectorAll('.roulette-item')).map(item => item.textContent);
    elements.push({
      element_type: 'roulette',
      position_x: parseInt(container.style.left) || 0,
      position_y: parseInt(container.style.top) || 0,
      width: parseInt(container.style.width),
      height: parseInt(container.style.height),
      element_config: {
        items: items
      }
    });
  });
  
  // タイマー
  slide.querySelectorAll('.timer-container').forEach(container => {
    const mode = container.getAttribute('data-timer-mode') || 'up';
    const targetSeconds = parseInt(container.getAttribute('data-timer-target')) || 0;
    const currentSeconds = parseInt(container.getAttribute('data-timer-seconds')) || 0;
    elements.push({
      element_type: 'timer',
      position_x: parseInt(container.style.left) || 0,
      position_y: parseInt(container.style.top) || 0,
      width: parseInt(container.style.width),
      height: parseInt(container.style.height),
      element_value: currentSeconds.toString(),
      element_config: {
        mode: mode,
        target: targetSeconds
      }
    });
  });
  
  // 図形
  slide.querySelectorAll('.shape-element').forEach(shape => {
    const shapeType = shape.getAttribute('data-shape-type');
    const shapeColor = shape.getAttribute('data-shape-color');
    const shapeFill = shape.getAttribute('data-shape-fill');
    
    let width, height;
    if (shapeType === 'triangle') {
      const borderBottom = parseInt(shape.style.borderBottomWidth) || 87;
      height = borderBottom;
      width = Math.floor(borderBottom * 100 / 87);
    } else {
      width = parseInt(shape.style.width);
      height = parseInt(shape.style.height);
    }
    
    elements.push({
      element_type: 'shape',
      position_x: parseInt(shape.style.left) || 0,
      position_y: parseInt(shape.style.top) || 0,
      width: width,
      height: height,
      element_config: {
        shape_type: shapeType,
        color: shapeColor,
        fill_color: shapeFill
      }
    });
  });
  
  // 画像
  slide.querySelectorAll('.image-element').forEach(imageContainer => {
    const imageSrc = imageContainer.getAttribute('data-image-src');
    elements.push({
      element_type: 'image',
      element_value: imageSrc, // Base64データまたはURL
      position_x: parseInt(imageContainer.style.left) || 0,
      position_y: parseInt(imageContainer.style.top) || 0,
      width: parseInt(imageContainer.style.width),
      height: parseInt(imageContainer.style.height)
    });
  });
  
  return elements;
}
```

#### restoreSystemElements() - _initialization.html

```javascript
function restoreSystemElements(elementsData) {
  if (!Array.isArray(elementsData)) {
    console.error('❌ elementsDataが配列ではありません:', elementsData);
    return;
  }
  
  console.log('📊 復元する要素数:', elementsData.length);
  
  elementsData.forEach(elem => {
    switch(elem.element_type) {
      case 'text_input':
        restoreTextInput(elem, false);
        break;
      case 'number_input':
        restoreTextInput(elem, true);
        break;
      case 'datetime_input':
        restoreDatetimeInput(elem);
        break;
      case 'checkbox_group':
        restoreCheckboxGroup(elem);
        break;
      case 'radio_group':
        restoreRadioGroup(elem);
        break;
      case 'button':
        restoreButton(elem);
        break;
      case 'text_box':
        restoreTextBox(elem);
        break;
      case 'roulette':
        restoreRoulette(elem);
        break;
      case 'timer':
        restoreTimer(elem);
        break;
      case 'shape':
        restoreShape(elem);
        break;
      case 'image':
        restoreImage(elem);
        break;
      default:
        console.warn('⚠️ 未知の要素タイプ:', elem.element_type);
    }
  });
}
```

#### restoreShape() - _initialization.html

```javascript
function restoreShape(elem) {
  const slide = document.getElementById('slideArea');
  if (!slide) return;

  const shapeType = elem.element_config?.shape_type || 'rectangle';
  const shapeColor = elem.element_config?.color || '#333333';
  const shapeFill = elem.element_config?.fill_color || 'transparent';

  const shape = document.createElement('div');
  shape.className = `shape-element shape-${shapeType}`;
  shape.setAttribute('data-shape-type', shapeType);
  shape.setAttribute('data-shape-color', shapeColor);
  shape.setAttribute('data-shape-fill', shapeFill);

  shape.style.left = elem.position_x + 'px';
  shape.style.top = elem.position_y + 'px';

  // 図形タイプに応じてサイズとスタイルを設定
  switch (shapeType) {
    case 'rectangle':
      shape.style.width = elem.width + 'px';
      shape.style.height = elem.height + 'px';
      shape.style.borderColor = shapeColor;
      shape.style.background = shapeFill;
      break;

    case 'circle':
      shape.style.width = elem.width + 'px';
      shape.style.height = elem.width + 'px';
      shape.style.borderColor = shapeColor;
      shape.style.background = shapeFill;
      break;

    case 'triangle':
      const height = elem.height || 87;
      const width = elem.width || 100;
      shape.style.width = '0px';
      shape.style.height = '0px';
      shape.style.borderLeftWidth = (width / 2) + 'px';
      shape.style.borderRightWidth = (width / 2) + 'px';
      shape.style.borderBottomWidth = height + 'px';
      shape.style.borderLeftColor = 'transparent';
      shape.style.borderRightColor = 'transparent';
      shape.style.borderBottomColor = shapeColor;
      shape.style.borderTopWidth = '0px';
      break;

    case 'line':
      shape.style.width = elem.width + 'px';
      shape.style.height = elem.height + 'px';
      shape.style.background = shapeColor;
      shape.style.border = 'none';
      break;

    case 'arrow':
      shape.style.width = elem.width + 'px';
      shape.style.height = elem.height + 'px';
      
      if (typeof updateArrowStyles === 'function') {
        updateArrowStyles(shape, shapeColor);
      } else {
        const styleId = 'arrow-' + Date.now();
        shape.setAttribute('data-style-id', styleId);
        const styleEl = document.createElement('style');
        styleEl.id = styleId;
        styleEl.textContent = `
          [data-style-id="${styleId}"]::before {
            content: '';
            flex: 1;
            height: 2px;
            background: ${shapeColor};
          }
          [data-style-id="${styleId}"]::after {
            content: '';
            width: 0;
            height: 0;
            border-left: 10px solid ${shapeColor};
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
          }
        `;
        document.head.appendChild(styleEl);
      }
      break;
  }

  shape.addEventListener('dblclick', function(e) {
    e.stopPropagation();
    if (typeof openShapeSettings === 'function') {
      openShapeSettings(shape);
    }
  });

  shape.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    e.stopPropagation();
    if (typeof openShapeSettings === 'function') {
      openShapeSettings(shape);
    }
  });

  addDragHandleIfMissing(shape);
  makeDraggable(shape);
  slide.appendChild(shape);

  if (typeof attachResizeHandlers === 'function') {
    attachResizeHandlers(shape, shapeType);
  }

  console.log('✅ 図形を復元:', { type: shapeType, color: shapeColor, x: elem.position_x, y: elem.position_y });
}
```

#### restoreImage() - _initialization.html

```javascript
function restoreImage(elem) {
  const slide = document.getElementById('slideArea');
  if (!slide) return;

  const imageSrc = elem.element_value;
  if (!imageSrc) {
    console.warn('⚠️ 画像のソースがありません');
    return;
  }

  const container = document.createElement('div');
  container.className = 'image-element';
  container.setAttribute('data-image-src', imageSrc);

  const img = document.createElement('img');
  img.src = imageSrc;
  img.style.pointerEvents = 'none';

  container.appendChild(img);

  container.style.left = elem.position_x + 'px';
  container.style.top = elem.position_y + 'px';
  container.style.width = elem.width + 'px';
  container.style.height = elem.height + 'px';

  container.addEventListener('dblclick', function(e) {
    e.stopPropagation();
    if (typeof openImageSettings === 'function') {
      openImageSettings(container);
    }
  });

  container.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    e.stopPropagation();
    if (typeof openImageSettings === 'function') {
      openImageSettings(container);
    }
  });

  addDragHandleIfMissing(container);
  makeDraggable(container);
  slide.appendChild(container);

  if (typeof attachResizeHandlers === 'function') {
    attachResizeHandlers(container, 'image');
  }

  console.log('✅ 画像を復元:', { src: imageSrc.substring(0, 50) + '...', x: elem.position_x, y: elem.position_y });
}
```

### Django設定（リクエストサイズ）

#### ファイル: `appproject/settings.py`

```python
# File upload settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# リクエストボディの最大サイズを設定（Base64画像データを含むため大きめに設定）
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_UPLOAD_EXTENSIONS = [
    # Images
    '.jpg', '.jpeg', '.png', '.gif',
    # Documents
    '.pdf', '.doc', '.docx', '.txt',
    # Archives
    '.zip', '.rar',
    # Code
    '.py', '.java', '.cpp', '.h'
]
```

**重要**: Base64エンコードされた画像データを含む要素データは3MB以上になることがあるため、`DATA_UPLOAD_MAX_MEMORY_SIZE`を10MBに設定。

---

## 🚀 実装ガイド（未実装部分）

### ふせいかい作成手順の実装

#### ステップ1: system/index.htmlに起動ロジック追加

**場所**: `accounts/templates/system/index.html` の `{% block extra_js %}`セクション末尾

```javascript
// ふせいかい作成チュートリアル起動処理
(function() {
  const shouldStartFuseikai = sessionStorage.getItem('tutorial_step2_fuseikai_create');
  console.log('🔍 tutorial_step2_fuseikai_create チェック:', shouldStartFuseikai);
  
  if (shouldStartFuseikai === 'true') {
    console.log('✅ ふせいかい作成チュートリアル開始準備');
    sessionStorage.removeItem('tutorial_step2_fuseikai_create');
    
    function initFuseikaiTutorial() {
      if (typeof tutorialOverlay === 'undefined') {
        console.error('❌ tutorialOverlay not found');
        return;
      }
      
      const shapeBtn = document.getElementById('shapeBtn');
      const saveBtn = document.getElementById('saveBtn');
      
      if (shapeBtn && saveBtn) {
        console.log('✅ 要素準備完了、ふせいかいチュートリアル開始');
        setTimeout(() => {
          startFuseikaiCreateTutorial();
        }, 500);
      } else {
        setTimeout(initFuseikaiTutorial, 500);
      }
    }
    
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initFuseikaiTutorial);
    } else {
      setTimeout(initFuseikaiTutorial, 1000);
    }
  }
})();
```

#### ステップ2: startFuseikaiCreateTutorial() 関数定義

**場所**: 同じく `{% block extra_js %}`セクション、startStep2Tutorial()の後

```javascript
function startFuseikaiCreateTutorial() {
  window.tutorialState = {
    isActive: true,
    targetColor: '#0000ff',  // 青色
    targetSize: 150
  };
  
  const steps = [
    // ステップ1: 開始メッセージ
    {
      target: null,
      centerMessage: true,
      message: 'つぎは「ふせいかい」がめんを つくりましょう！<br><br>さんかくの かたちを つかいます。',
      nextText: 'つぎへ'
    },
    
    // ステップ2: 図形ボタンクリック
    {
      target: '#shapeBtn',
      message: 'ずけい ボタンを クリックして ください！',
      messagePosition: 'left',
      requireClick: true,
      onNext: function() {
        const shapeBtn = document.getElementById('shapeBtn');
        if (shapeBtn && (!shapeBtn.getAttribute('aria-expanded') || shapeBtn.getAttribute('aria-expanded') === 'false')) {
          shapeBtn.click();
        }
        setTimeout(() => tutorialOverlay.next(), 300);
      }
    },
    
    // ステップ3: 三角ボタンクリック
    {
      target: '#addTriangleBtn',
      message: 'メニューから「さんかく」を クリックして ください！',
      requireClick: true,
      onNext: function() {
        let checkCount = 0;
        const maxChecks = 20;
        
        const waitForTriangle = setInterval(() => {
          checkCount++;
          const triangles = document.querySelectorAll('[data-shape-type="triangle"]');
          
          if (triangles.length > 0 || checkCount >= maxChecks) {
            clearInterval(waitForTriangle);
            
            if (triangles.length > 0) {
              const lastTriangle = triangles[triangles.length - 1];
              window.tutorialState.createdTriangle = lastTriangle;
              window.tutorialState.canvas = document.querySelector('.main-area');
              setTimeout(() => tutorialOverlay.next(), 500);
            } else {
              console.warn('⚠️ 三角が見つかりませんでした');
              tutorialOverlay.next();
            }
          }
        }, 100);
      }
    },
    
    // ステップ4: 三角の右クリック指示
    {
      target: '.main-area',
      centerMessage: false,
      message: 'さんかくが でてきましたね！<br><br>この さんかくを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。',
      messagePosition: 'left',
      nextText: null,
      showSkip: false,
      onShow: function() {
        const triangle = window.tutorialState.createdTriangle;
        
        if (triangle) {
          tutorialOverlay.positionHighlight(triangle);
          tutorialOverlay.positionOverlayParts(triangle);
          
          // メッセージ位置調整（せいかいと同じロジック）
          const triangleRect = triangle.getBoundingClientRect();
          const messageBox = tutorialOverlay.messageBox;
          
          messageBox.innerHTML = `
            <div class="tutorial-step-indicator">
              STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
            </div>
            <div class="tutorial-message-content">
              さんかくが でてきましたね！<br><br>この さんかくを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。
            </div>
            <div class="tutorial-buttons">
              <button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>
            </div>
          `;
          
          const viewportWidth = window.innerWidth;
          const viewportHeight = window.innerHeight;
          
          messageBox.style.display = 'block';
          messageBox.style.visibility = 'hidden';
          const messageRect = messageBox.getBoundingClientRect();
          
          let left = triangleRect.left - messageRect.width - 20;
          let top = triangleRect.top;
          
          if (left < 20) {
            left = triangleRect.right + 20;
            if (left + messageRect.width > viewportWidth - 20) {
              left = triangleRect.left;
              top = triangleRect.bottom + 20;
            }
          }
          
          if (top + messageRect.height > viewportHeight - 20) {
            top = viewportHeight - messageRect.height - 20;
          }
          if (top < 20) {
            top = 20;
          }
          
          messageBox.style.top = `${top}px`;
          messageBox.style.left = `${left}px`;
          messageBox.style.visibility = 'visible';
          messageBox.className = 'tutorial-message';
          
          // 編集パネル監視
          const checkForPanel = setInterval(() => {
            const panel = document.querySelector('.shape-settings-panel');
            if (panel) {
              clearInterval(checkForPanel);
              setTimeout(() => tutorialOverlay.next(), 300);
            }
          }, 100);
        }
      }
    },
    
    // ステップ5: 色と大きさ変更
    {
      target: '.shape-settings-panel',
      centerMessage: false,
      message: 'すばらしい！<br><br>それでは、さんかくの「いろ」と「おおきさ」を かえましょう！<br><br><strong>【いろ】</strong><br>RGBで <strong>0, 0, 255</strong> と にゅうりょくするか、<br>カラーピッカーで <strong>あお</strong>を えらんでください。<br><br><strong>【おおきさ】</strong><br><strong>150</strong> に してください。<br><br>できたら、したの <strong>「てきよう」ボタン</strong>を おしてください！',
      messagePosition: 'left',
      nextText: null,
      showSkip: false,
      onShow: function() {
        const panel = document.querySelector('.shape-settings-panel');
        if (panel) {
          tutorialOverlay.positionHighlight(panel);
          tutorialOverlay.positionOverlayParts(panel);
          
          const rect = panel.getBoundingClientRect();
          const messageBox = tutorialOverlay.messageBox;
          
          messageBox.style.display = 'block';
          messageBox.style.left = '20px';
          messageBox.style.top = `${Math.max(20, rect.top)}px`;
          messageBox.style.visibility = 'visible';
          
          const checkApplyButton = setInterval(() => {
            const applyBtn = document.getElementById('shapeApplyBtn');
            
            if (applyBtn && !applyBtn.dataset.tutorialListenerAdded) {
              applyBtn.dataset.tutorialListenerAdded = 'true';
              
              const applyClickHandler = function(e) {
                clearInterval(checkApplyButton);
                setTimeout(() => tutorialOverlay.next(), 500);
                applyBtn.removeEventListener('click', applyClickHandler);
                delete applyBtn.dataset.tutorialListenerAdded;
              };
              
              applyBtn.addEventListener('click', applyClickHandler);
            }
          }, 100);
        }
      }
    },
    
    // ステップ6: フォームボタンクリック
    {
      target: '#formBtn',
      message: 'すばらしい！<br><br>つぎは もじを いれる はこを つくります。<br>この フォーム ボタンを クリックして ください！',
      messagePosition: 'left',
      requireClick: true,
      onNext: function() {
        const formBtn = document.getElementById('formBtn');
        if (formBtn && (!formBtn.getAttribute('aria-expanded') || formBtn.getAttribute('aria-expanded') === 'false')) {
          formBtn.click();
        }
        setTimeout(() => tutorialOverlay.next(), 300);
      }
    },
    
    // ステップ7: テキストボックスボタンクリック
    {
      target: '#addTextBoxBtn',
      message: 'メニューから「テキストボックス」を クリックして ください！',
      messagePosition: 'left',
      requireClick: true,
      onNext: function() {
        setTimeout(() => tutorialOverlay.next(), 300);
      }
    },
    
    // ステップ8: テキストボックス配置
    {
      target: '.main-area',
      centerMessage: false,
      message: 'がめんを クリックして、<br>カーソルを うごかして、<br>テキストボックスを はいち してください！',
      messagePosition: 'left',
      nextText: null,
      showSkip: false,
      onShow: function() {
        const initialTextBoxCount = document.querySelectorAll('.text-box-container').length;
        window.tutorialState.initialTextBoxCount = initialTextBoxCount;
        
        const checkTextBoxPlacement = setInterval(() => {
          const textBoxes = document.querySelectorAll('.text-box-container');
          
          if (textBoxes.length > initialTextBoxCount) {
            clearInterval(checkTextBoxPlacement);
            window.tutorialState.createdTextBox = textBoxes[textBoxes.length - 1];
            setTimeout(() => tutorialOverlay.next(), 500);
          }
        }, 100);
      }
    },
    
    // ステップ9: テキスト入力
    {
      target: '.text-box-container',
      centerMessage: false,
      message: 'テキストボックスが はいち できましたね！<br><br>このテキストボックスを クリックして、<br>「ふせいかい！」と にゅうりょく してください！',
      messagePosition: 'right',
      nextText: null,
      showSkip: false,
      onShow: function() {
        const textBox = window.tutorialState.createdTextBox;
        
        if (textBox) {
          tutorialOverlay.positionHighlight(textBox);
          tutorialOverlay.positionOverlayParts(textBox);
          
          // メッセージ位置調整（せいかいと同じロジック）
          const rect = textBox.getBoundingClientRect();
          const messageBox = tutorialOverlay.messageBox;
          
          messageBox.innerHTML = `
            <div class="tutorial-step-indicator">
              STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
            </div>
            <div class="tutorial-message-content">
              テキストボックスが はいち できましたね！<br><br>このテキストボックスを クリックして、<br>「ふせいかい！」と にゅうりょく してください！
            </div>
            <div class="tutorial-buttons">
              <button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>
            </div>
          `;
          
          const viewportWidth = window.innerWidth;
          const viewportHeight = window.innerHeight;
          
          messageBox.style.display = 'block';
          messageBox.style.visibility = 'hidden';
          const messageRect = messageBox.getBoundingClientRect();
          
          let left = rect.right + 20;
          let top = rect.top;
          
          if (left + messageRect.width > viewportWidth - 20) {
            left = rect.left - messageRect.width - 20;
            if (left < 20) {
              left = rect.left;
              top = rect.bottom + 20;
            }
          }
          
          if (top + messageRect.height > viewportHeight - 20) {
            top = viewportHeight - messageRect.height - 20;
          }
          if (top < 20) {
            top = 20;
          }
          
          messageBox.style.top = `${top}px`;
          messageBox.style.left = `${left}px`;
          messageBox.style.visibility = 'visible';
          messageBox.className = 'tutorial-message';
        }
        
        // テキスト入力検出
        const checkTextInput = setInterval(() => {
          const textAreas = document.querySelectorAll('.text-box');
          let textCorrect = false;
          
          textAreas.forEach(textArea => {
            const value = textArea.value.trim();
            if (value.includes('ふせいかい！') || 
                value.includes('ふせいかい!') || 
                value.includes('ふせいかい')) {
              textCorrect = true;
            }
          });
          
          if (textCorrect) {
            clearInterval(checkTextInput);
            setTimeout(() => tutorialOverlay.next(), 500);
          }
        }, 100);
      }
    },
    
    // ステップ10: 保存ボタンクリック
    {
      target: '#saveBtn',
      message: 'よくできました！<br><br>それでは、ほぞんボタンを おして、<br>「ふせいかい」という なまえで ほぞん してください！',
      nextText: 'わかった',
      showNextButton: false,
      onShow: function() {
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
          tutorialOverlay.positionHighlight(saveBtn);
          tutorialOverlay.positionOverlayParts(saveBtn);
          
          const saveClickHandler = function(e) {
            tutorialOverlay.end();
            sessionStorage.setItem('tutorial_step2_fuseikai_save', 'true');
            console.log('📝 tutorial_step2_fuseikai_save フラグを設定しました');
            saveBtn.removeEventListener('click', saveClickHandler);
          };
          
          saveBtn.addEventListener('click', saveClickHandler);
        }
      }
    }
  ];
  
  tutorialOverlay.init(steps, {
    onComplete: function() {
      console.log('✅ ふせいかい作成チュートリアル完了');
    },
    onSkip: function() {
      if (confirm('チュートリアルを とちゅうで やめますか？')) {
        fetch('/accounts/skip-tutorial-step/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ step: 2 })
        });
        return true;
      }
      return false;
    }
  });
}
```

#### ステップ3: system_create.htmlにふせいかい保存チュートリアル追加

**場所**: `accounts/templates/system/system_create.html` の `{% block extra_js %}`セクション末尾

```javascript
// ふせいかい保存チュートリアル起動処理
document.addEventListener('DOMContentLoaded', function() {
  const shouldStartTutorial = sessionStorage.getItem('tutorial_step2_fuseikai_save');
  console.log('📋 tutorial_step2_fuseikai_save:', shouldStartTutorial);
  
  if (shouldStartTutorial === 'true') {
    console.log('✅ ふせいかい保存チュートリアルを開始します');
    sessionStorage.removeItem('tutorial_step2_fuseikai_save');
    
    setTimeout(() => {
      startSaveFuseikaiTutorial();
    }, 500);
  }
});

function startSaveFuseikaiTutorial() {
  const tutorialSteps = [
    {
      message: `
        <div style="text-align: center;">
          <div style="font-size: 28px; font-weight: 800; color: #3fbcd9; margin-bottom: 15px;">
            📝 システムのなまえをいれよう！
          </div>
          <div style="font-size: 18px; line-height: 1.8; color: #2d3748;">
            「ふせいかい」と いれてね！
          </div>
        </div>
      `,
      target: '#systemName',
      centerMessage: false,
      showNextButton: false,
      onShow: function() {
        const nameInput = document.getElementById('systemName');
        if (nameInput) {
          tutorialOverlay.positionHighlight(nameInput);
          tutorialOverlay.positionOverlayParts(nameInput);
          
          const checkNameInput = setInterval(() => {
            const value = nameInput.value.trim();
            
            if (value.includes('ふせいかい')) {
              clearInterval(checkNameInput);
              setTimeout(() => tutorialOverlay.next(), 500);
            }
          }, 100);
        }
      }
    },
    
    {
      message: `
        <div style="text-align: center;">
          <div style="font-size: 28px; font-weight: 800; color: #3fbcd9; margin-bottom: 15px;">
            💾 ほぞんしよう！
          </div>
          <div style="font-size: 18px; line-height: 1.8; color: #2d3748;">
            「ほぞんする」ボタンを おしてね！
          </div>
        </div>
      `,
      target: '#saveBtn',
      centerMessage: false,
      showNextButton: false,
      onShow: function() {
        const saveBtn = document.getElementById('saveBtn');
        if (saveBtn) {
          tutorialOverlay.positionHighlight(saveBtn);
          tutorialOverlay.positionOverlayParts(saveBtn);
          
          const saveClickHandler = function(e) {
            tutorialOverlay.end();
            sessionStorage.setItem('tutorial_step2_mondai_create', 'true');
            console.log('📝 tutorial_step2_mondai_create フラグを設定しました');
            saveBtn.removeEventListener('click', saveClickHandler);
          };
          
          saveBtn.addEventListener('click', saveClickHandler);
        }
      }
    }
  ];
  
  tutorialOverlay.init(tutorialSteps);
}
```

### その他の未実装部分

もんだい作成、アルゴリズム作成、テスト実行の実装パターンは、上記のふせいかい作成と同じ構造になります:

1. **起動ロジック**: sessionStorage検出 → DOMContentLoaded対応 → 関数呼び出し
2. **チュートリアル関数**: ステップ配列定義 → tutorialOverlay.init()
3. **ステップ定義**: target指定 → onShow/onNextでロジック → 検出処理（setInterval） → next()
4. **次のフラグ設定**: 最終ステップで次のsessionStorageフラグを設定

**重要な注意点**:
- 必ず`clearInterval()`を呼び、メモリリークを防ぐ
- イベントリスナーは必ず削除する（`removeEventListener()`）
- `dataset.tutorialListenerAdded`で重複登録を防止
- デバッグログを豊富に出力（🔍、✅、❌など）
- タイムアウト処理を追加（最大チェック回数 `maxChecks`）

---

## 🐛 デバッグ手法

### コンソールログの活用

```javascript
// チュートリアル起動
console.log('🔍 tutorial_step2_xxx チェック:', sessionStorage.getItem('tutorial_step2_xxx'));
console.log('✅ チュートリアル開始準備');

// 要素検出
console.log('🔍 ターゲット要素を検索:', selector);
console.log('✅ ターゲット要素が見つかりました:', element);
console.log('❌ ターゲット要素が見つかりません:', selector);

// ステップ進行
console.log(`📍 showStep(${stepIndex}) called`);
console.log(`📋 ステップ ${stepIndex} の情報:`, {...});
console.log('➡️ 次のステップへ進みます');
console.log('✅ next()呼び出し完了');

// 操作検出
console.log('🔍 検出処理開始');
console.log('✅ 円が配置されました:', circle);
console.log('✅ 編集パネルが開きました');
console.log('✅ テキストが入力されました');

// エラー
console.error('❌ エラー:', error);
console.warn('⚠️ 警告:', warning);
```

### sessionStorageの確認

```javascript
// ブラウザ開発者ツール > Application > Storage > Session Storage
// または
console.log('📦 sessionStorage:', {
  tutorial_step2_start: sessionStorage.getItem('tutorial_step2_start'),
  tutorial_step2_seikai_save: sessionStorage.getItem('tutorial_step2_seikai_save'),
  systemDesignContent: sessionStorage.getItem('systemDesignContent')?.substring(0, 100) + '...'
});
```

### トラブルシューティング

**問題: チュートリアルが起動しない**
1. sessionStorageフラグを確認
2. DOMContentLoadedのタイミングを確認
3. tutorialOverlayの読み込みを確認
4. ターゲット要素の存在を確認

**問題: ステップが進まない**
1. onShowコールバックの実行を確認
2. setIntervalが動作しているか確認
3. 検出条件を確認（要素数、テキスト内容など）
4. clearInterval()が呼ばれているか確認

**問題: メッセージボックスの位置がおかしい**
1. getBoundingClientRect()の値を確認
2. viewport調整を確認
3. messagePositionの指定を試す

---

## 📝 チェックリスト（実装時）

### コード品質

- [ ] console.logで豊富なデバッグ情報を出力
- [ ] setIntervalを必ずclearInterval()で停止
- [ ] イベントリスナーを必ず削除
- [ ] `dataset.tutorialListenerAdded`で重複登録防止
- [ ] タイムアウト処理を実装（maxChecks）
- [ ] エラーハンドリング（要素未発見時の処理）

### ユーザビリティ

- [ ] ひらがな・カタカナ多用
- [ ] メッセージは短く、わかりやすく
- [ ] ステップ表示で進捗を明示
- [ ] スキップボタンを適切に配置
- [ ] 自動進行で操作負担を軽減

### テスト

- [ ] 正常系: 指示通りの操作で進行
- [ ] 異常系: 意図しない操作でもエラーにならない
- [ ] スキップ: いつでもスキップ可能
- [ ] 再開: ページリロード後も継続可能（sessionStorage）
- [ ] 複数ブラウザ: Chrome, Firefox, Edge

---

## 🎓 学習リソース

### sessionStorage API
- [MDN Web Docs - sessionStorage](https://developer.mozilla.org/ja/docs/Web/API/Window/sessionStorage)

### setInterval / clearInterval
- [MDN Web Docs - setInterval](https://developer.mozilla.org/ja/docs/Web/API/setInterval)
- [MDN Web Docs - clearInterval](https://developer.mozilla.org/ja/docs/Web/API/clearInterval)

### addEventListener / removeEventListener
- [MDN Web Docs - addEventListener](https://developer.mozilla.org/ja/docs/Web/API/EventTarget/addEventListener)
- [MDN Web Docs - removeEventListener](https://developer.mozilla.org/ja/docs/Web/API/EventTarget/removeEventListener)

### Blockly
- [Blockly Developer Tools](https://developers.google.com/blockly)

---

## 📞 サポート

このドキュメントに不明点がある場合や、実装中に問題が発生した場合は、以下を確認してください:

1. **人間用ガイド**: `TUTORIAL_STEP2_GUIDE.md`
2. **既存コード**: 実装済みのせいかい作成手順を参照
3. **デバッグログ**: コンソールログで詳細を確認

---

**最終更新**: 2026-02-05  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot Chat
