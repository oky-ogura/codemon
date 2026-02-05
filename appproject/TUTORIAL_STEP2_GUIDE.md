# STEP2チュートリアル 開発ガイド（人間用）

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [チュートリアルの設計思想](#チュートリアルの設計思想)
3. [全体フロー](#全体フロー)
4. [STEP1: karihomeでのチュートリアル](#step1-karihomeでのチュートリアル)
5. [STEP2: システム作成チュートリアル](#step2-システム作成チュートリアル)
6. [実装状況](#実装状況)
7. [各機能の詳細仕様](#各機能の詳細仕様)
8. [デバッグとトラブルシューティング](#デバッグとトラブルシューティング)
9. [今後の作業項目](#今後の作業項目)

---

## プロジェクト概要

### 目的
小学生向けのプログラミング学習アプリ「Codemon」において、クイズシステム作成の操作を段階的に学習できるチュートリアルを実装する。

### ターゲット
- 小学生（低学年〜高学年）
- プログラミング初心者

### チュートリアルの最終ゴール
ユーザーが以下を自力で作成できるようになること：
- 3つのシステムファイル（問題、正解、不正解）
- 1つのアルゴリズム（条件分岐によるクイズ判定）
- 実行テストと保存まで完了

---

## チュートリアルの設計思想

### 基本コンセプト
1. **ステップバイステップ**: 1つの操作ごとに明確な指示
2. **視覚的フィードバック**: ハイライトとオーバーレイで操作箇所を明示
3. **やさしい言葉**: ひらがな多用、難しい用語を避ける
4. **自動進行**: 可能な限り操作を検出して自動で次へ
5. **成功体験**: 各ステップで達成感を味わえる

### UI/UXの特徴

#### オーバーレイシステム
- **4分割オーバーレイ**: 画面を上下左右4つに分割し、操作対象以外を暗く表示
- **ハイライト枠**: 操作対象を明るく表示（パディング10px）
- **z-index階層**:
  - オーバーレイ: 10000
  - ハイライト: 10001
  - 操作対象: 10002
  - メッセージボックス: 10003

#### メッセージボックス
- **位置調整**: ターゲット要素の下、上、左、右、または画面中央
- **ドラッグ可能**: ユーザーが好きな位置に移動できる
- **矢印表示**: ターゲット要素への方向を視覚的に示す
- **ステップ表示**: 「STEP X / Y」で進捗を表示

#### 操作検出
- **クリック検出**: `requireClick: true` でクリック待機
- **入力検出**: テキスト内容を100msごとにポーリング
- **パネル検出**: 編集パネルの開閉を100msごとに監視
- **要素追加検出**: DOM要素の追加を100msごとに確認

---

## 全体フロー

### チュートリアルの開始から終了まで

```
[karihome画面]
   ↓ システムボタンクリック
[system_choice画面]
   ↓ 「新しく作る」ボタンクリック
   ↓ sessionStorage設定: tutorial_step2_start = 'true'
[system/index.html]
   ↓ チュートリアル開始（STEP2）
   │
   ├─ せいかい画面作成
   │   ├─ 円図形作成（赤色、150px）
   │   ├─ テキストボックス作成（「せいかい!」）
   │   └─ 保存（システム名「せいかい」）
   │
   ├─ system_create.html
   │   └─ せいかい保存チュートリアル
   │       └─ sessionStorage設定: tutorial_step2_fuseikai_create = 'true'
   │
   ├─ system_list.html
   │   └─ 「新しく作る」ボタンクリック
   │
   ├─ ふせいかい画面作成
   │   ├─ 三角図形作成（青色、150px）
   │   ├─ テキストボックス作成（「ふせいかい!」）
   │   └─ 保存（システム名「ふせいかい」）
   │
   ├─ system_list.html
   │   └─ 「新しく作る」ボタンクリック
   │
   ├─ もんだい画面作成
   │   ├─ チェックボックス作成（「1+1は?」、項目: 1,2,3）
   │   ├─ ボタン作成
   │   └─ ボタン右クリック → アルゴリズム新規作成
   │
   ├─ アルゴリズム作成画面（block.html）
   │   ├─ 「もしシステム〇〇の～」ブロック配置
   │   ├─ システム選択（仮保存_日時、1+1、項目:2）
   │   ├─ 「システムを表示」ブロック配置（せいかい）
   │   ├─ 「システムを表示」ブロックをコピー（ふせいかい）
   │   └─ 保存（アルゴリズム名「チュートリアル」）
   │
   ├─ もんだい画面に戻る
   │   ├─ 実行テスト（2をチェック → せいかい画面）
   │   ├─ 実行テスト（3をチェック → ふせいかい画面）
   │   └─ 保存（システム名「もんだい」）
   │
[karihome画面]
   └─ STEP2チュートリアル完了
```

---

## STEP1: karihomeでのチュートリアル

### 実装ファイル
- `accounts/templates/accounts/karihome.html`

### チュートリアル内容
（STEP1の詳細はここに記載 - 現時点ではSTEP2に焦点）

---

## STEP2: システム作成チュートリアル

### 2-1. せいかい画面作成

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_start') === 'true'`
- **設定場所**: `system_choice.html` の「新しく作る」ボタンクリック時
- **実行場所**: `system/index.html`

#### チュートリアルステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | チュートリアル開始メッセージ | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 2 | 実行ボタンの説明 | `#executeBtn` | 「わかった」ボタン | ボタンクリック |
| 3 | 保存ボタンの説明 | `#saveBtn` | 「わかった」ボタン | ボタンクリック |
| 4 | せいかい画面作成開始 | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 5 | 図形ボタンクリック | `#shapeBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 6 | 円ボタンクリック | `#addCircleBtn` | ボタンクリック | 円要素の追加検出 + 自動進行 |
| 7 | 円の右クリック指示 | `.main-area`（円をハイライト） | 円を右クリック | 編集パネルの開閉検出 + 自動進行 |
| 8 | 色と大きさ変更 | `.shape-settings-panel` | RGB(255,0,0)、サイズ150px、適用ボタン | 適用ボタンクリック検出 + 自動進行 |
| 9 | フォームボタンクリック | `#formBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 10 | テキストボックスボタンクリック | `#addTextBoxBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 11 | テキストボックス配置 | `.main-area` | 画面クリック | テキストボックス要素の追加検出 + 自動進行 |
| 12 | テキスト入力 | `.text-box-container` | 「せいかい!」と入力 | テキスト内容の検出 + 自動進行 |
| 13 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_seikai_save`設定 |

#### 重要な実装ポイント

**ステップ7（円の右クリック指示）の工夫**
- ターゲットは`.main-area`（キャンバス全体）だが、ハイライトは円に対して行う
- メッセージボックスを円の左側に配置
- 編集パネルの開閉を100msごとに監視し、開いたら自動進行

**ステップ8（色と大きさ変更）の工夫**
- 編集パネル全体をハイライト
- メッセージボックスを左側に固定（パネルが右側に表示されるため）
- 適用ボタンに一時的なイベントリスナーを追加
  ```javascript
  applyBtn.addEventListener('click', applyClickHandler);
  ```
- `dataset.tutorialListenerAdded`フラグで重複登録を防止

**ステップ12（テキスト入力）の検出ロジック**
```javascript
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
    tutorialOverlay.next();
  }
}, 100);
```

### 2-2. せいかい保存画面

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_seikai_save') === 'true'`
- **設定場所**: `system/index.html` のステップ13（保存ボタンクリック時）
- **実行場所**: `system_create.html`

#### チュートリアルステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | システム名入力指示 | `#systemName` | 「せいかい」と入力 | 入力内容検出 + 自動進行 |
| 2 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_fuseikai_create`設定 |

#### 重要な実装ポイント

**ステップ1（システム名入力）**
```javascript
const checkNameInput = setInterval(() => {
  const value = nameInput.value.trim();
  if (value.includes('せいかい')) {
    clearInterval(checkNameInput);
    setTimeout(() => tutorialOverlay.next(), 500);
  }
}, 100);
```

**ステップ2（保存ボタンクリック）**
- 保存ボタンクリック時に`tutorial_step2_fuseikai_create`フラグを設定
- チュートリアルを終了し、通常の保存処理を続行

### 2-3. ふせいかい画面作成（未実装）

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_fuseikai_create') === 'true'`
- **設定場所**: `system_create.html` の保存ボタンクリック時
- **実行場所**: `system/index.html`（system_listから遷移後）

#### 予定ステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | ふせいかい画面作成開始 | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 2 | 図形ボタンクリック | `#shapeBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 3 | 三角ボタンクリック | `#addTriangleBtn` | ボタンクリック | 三角要素の追加検出 + 自動進行 |
| 4 | 三角の右クリック指示 | `.main-area`（三角をハイライト） | 三角を右クリック | 編集パネルの開閉検出 + 自動進行 |
| 5 | 色と大きさ変更 | `.shape-settings-panel` | RGB(0,0,255)、サイズ150px、適用ボタン | 適用ボタンクリック検出 + 自動進行 |
| 6 | フォームボタンクリック | `#formBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 7 | テキストボックスボタンクリック | `#addTextBoxBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 8 | テキストボックス配置 | `.main-area` | 画面クリック | テキストボックス要素の追加検出 + 自動進行 |
| 9 | テキスト入力 | `.text-box-container` | 「ふせいかい!」と入力 | テキスト内容の検出 + 自動進行 |
| 10 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_fuseikai_save`設定 |

#### ふせいかい保存画面（未実装）

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | システム名入力指示 | `#systemName` | 「ふせいかい」と入力 | 入力内容検出 + 自動進行 |
| 2 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_mondai_create`設定 |

### 2-4. もんだい画面作成（未実装）

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_mondai_create') === 'true'`
- **設定場所**: `system_create.html`（ふせいかい保存後）
- **実行場所**: `system/index.html`（system_listから遷移後）

#### 予定ステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | もんだい画面作成開始 | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 2 | フォームボタンクリック | `#formBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 3 | チェックボックスボタンクリック | `#addCheckboxBtn` | ボタンクリック | チェックボックスパネル開閉検出 + 自動進行 |
| 4 | ラベル入力 | チェックボックス設定パネル | 「1+1は?」と入力 | 入力内容検出 |
| 5 | 項目数確認 | チェックボックス設定パネル | 項目数3のまま | 「作成」ボタンクリック待機 |
| 6 | 作成ボタンクリック | チェックボックス設定パネル | ボタンクリック | チェックボックス要素の追加検出 + 自動進行 |
| 7 | 項目1編集 | チェックボックス項目1 | 「1」と入力 | 入力内容検出 + 自動進行 |
| 8 | 項目2編集 | チェックボックス項目2 | 「2」と入力 | 入力内容検出 + 自動進行 |
| 9 | 項目3編集 | チェックボックス項目3 | 「3」と入力 | 入力内容検出 + 自動進行 |
| 10 | ボタン機能クリック | `#buttonBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 11 | ボタン作成 | ボタン設定パネル | そのまま作成ボタンクリック | ボタン要素の追加検出 + 自動進行 |
| 12 | ボタン右クリック | 作成したボタン要素 | 右クリック | コンテキストメニュー検出 + 自動進行 |
| 13 | アルゴリズム新規作成 | コンテキストメニュー | 「アルゴリズムを新規作成」クリック | クリック検出 + `tutorial_step2_algorithm_create`設定 |

### 2-5. アルゴリズム作成（未実装）

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_algorithm_create') === 'true'`
- **設定場所**: `system/index.html`（ボタン右クリック後）
- **実行場所**: `block.html`

#### 予定ステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | アルゴリズム作成開始 | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 2 | システム機能タブクリック | システム機能タブ | クリック | クリック検出 + 自動進行 |
| 3 | 「もしシステム〇〇の～」ブロッククリック | 該当ブロック | クリック | ワークスペースへの配置検出 + 自動進行 |
| 4 | システム選択（仮保存） | ブロック内リスト1 | 「仮保存_日時」を選択 | 選択変更検出 + 自動進行 |
| 5 | 項目選択（1+1） | ブロック内リスト2 | 「1+1は?」を選択 | 選択変更検出 + 自動進行 |
| 6 | 選択肢選択（2） | ブロック内リスト3 | 「項目:2」を選択 | 選択変更検出 + 自動進行 |
| 7 | システムタブクリック | システムタブ | クリック | クリック検出 + 自動進行 |
| 8 | 「システムを表示」ブロッククリック | 該当ブロック | クリック | ワークスペースへの配置検出 + 自動進行 |
| 9 | システム選択（せいかい） | ブロック内リスト | 「せいかい」を選択 | 選択変更検出 + 自動進行 |
| 10 | ブロックをドラッグ | 配置したブロック | 「すること」の穴にドラッグ | 接続検出 + 自動進行 |
| 11 | ブロック右クリック | 配置したブロック | 右クリック | コンテキストメニュー検出 + 自動進行 |
| 12 | ブロックコピー | コンテキストメニュー | 「コピーする」クリック | クリック検出 + 自動進行 |
| 13 | システム選択変更（ふせいかい） | コピーしたブロック | 「ふせいかい」を選択 | 選択変更検出 + 自動進行 |
| 14 | ブロックをドラッグ | コピーしたブロック | 「そうでなければ」の穴にドラッグ | 接続検出 + 自動進行 |
| 15 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_algorithm_save`設定 |

#### アルゴリズム保存画面（未実装）

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | アルゴリズム名入力 | アルゴリズム名フィールド | 「チュートリアル」と入力 | 入力内容検出 |
| 2 | 詳細入力 | 詳細フィールド | 「チュートリアルぶんき」と入力 | 入力内容検出 |
| 3 | 保存するボタンクリック | 保存ボタン | ボタンクリック | クリック検出 + ダイアログ検出 |
| 4 | ダイアログOKクリック | ダイアログOKボタン | ボタンクリック | クリック検出 + `tutorial_step2_test_execute`設定 |

### 2-6. テスト実行と保存（未実装）

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_test_execute') === 'true'`
- **設定場所**: `block.html`（アルゴリズム保存後）
- **実行場所**: `system/index.html`（もんだい画面）

#### 予定ステップ

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | テスト実行開始 | なし（画面中央） | 「つぎへ」ボタン | ボタンクリック |
| 2 | 実行ボタンクリック | `#executeBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 3 | チェックボックス2にチェック | チェックボックス項目2 | チェック | チェック状態検出 + 自動進行 |
| 4 | ボタンクリック | 作成したボタン | ボタンクリック | クリック検出 + せいかい画面遷移検出 |
| 5 | せいかい画面確認 | せいかい画面 | 「つぎへ」ボタン | ボタンクリック |
| 6 | 閉じるボタンクリック | 閉じるボタン | ボタンクリック | クリック検出 + もんだい画面復帰検出 |
| 7 | 実行ボタンクリック（2回目） | `#executeBtn` | ボタンクリック | クリック検出 + 自動進行 |
| 8 | チェックボックス3にチェック | チェックボックス項目3 | チェック | チェック状態検出 + 自動進行 |
| 9 | ボタンクリック | 作成したボタン | ボタンクリック | クリック検出 + ふせいかい画面遷移検出 |
| 10 | ふせいかい画面確認 | ふせいかい画面 | 「つぎへ」ボタン | ボタンクリック |
| 11 | 閉じるボタンクリック | 閉じるボタン | ボタンクリック | クリック検出 + もんだい画面復帰検出 |
| 12 | 保存ボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_mondai_save`設定 |

#### もんだい保存画面（未実装）

| ステップ | 内容 | ターゲット要素 | 操作 | 次へ進む条件 |
|---------|------|--------------|------|------------|
| 1 | システム名入力指示 | `#systemName` | 「もんだい」と入力 | 入力内容検出 + 自動進行 |
| 2 | 詳細入力指示 | `#systemDetail` | 「チュートリアルもんだい」と入力 | 入力内容検出 + 自動進行 |
| 3 | 保存するボタンクリック | `#saveBtn` | ボタンクリック | クリック検出 + `tutorial_step2_complete`設定 |
| 4 | メイン画面へボタンクリック | メイン画面へボタン | ボタンクリック | クリック検出 + karihome遷移 |

### 2-7. STEP2完了

#### 起動タイミング
- **トリガー**: `sessionStorage.getItem('tutorial_step2_complete') === 'true'`
- **実行場所**: `karihome.html`

#### 完了メッセージ表示
```javascript
// karihome.htmlで完了メッセージを表示
const tutorialSteps = [
  {
    target: null,
    centerMessage: true,
    message: 'おめでとうございます！<br><br>STEP2のチュートリアルが かんりょう しました！<br><br>これで クイズシステムを じぶんで つくれるように なりましたね！',
    nextText: 'わかった',
    onNext: function() {
      // STEP2完了フラグをサーバーに送信
      fetch('/accounts/complete-tutorial-step/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ step: 2 })
      });
      sessionStorage.removeItem('tutorial_step2_complete');
    }
  }
];
```

---

## 実装状況

### ✅ 完了した項目

#### STEP2基本構造
- オーバーレイシステム（4分割、ハイライト）
- メッセージボックス（位置調整、ドラッグ機能）
- TutorialOverlayクラス（tutorial_overlay.js）
- チュートリアルCSS（tutorial_overlay.css）

#### せいかい作成手順
1. ✅ 実行ボタン・保存ボタン説明
2. ✅ 図形ボタンクリック → 円ボタンクリック
3. ✅ 円の配置検出
4. ✅ 円の右クリック指示（パネル左寄せ）
5. ✅ 円フォーカス（メッセージ位置調整）
6. ✅ 色・大きさ変更（適用ボタン監視）
7. ✅ テキストボックス作成（フォームボタン → テキストボックスボタン → 配置）
8. ✅ テキスト入力検出（「せいかい!」）
9. ✅ 保存ボタンクリック

#### せいかい保存画面
1. ✅ システム名入力検出（「せいかい」）
2. ✅ 保存ボタンクリック → ふせいかい作成フラグ設定

#### チュートリアル起動修正
- ✅ sessionStorage設定タイミング修正
- ✅ DOMContentLoaded対応
- ✅ デバッグログ大幅追加
- ✅ requireClick修正

#### 保存・復元機能修正
- ✅ 図形・画像の収集処理実装（collectCurrentElements）
- ✅ 図形・画像の復元処理実装（restoreShape、restoreImage）
- ✅ リクエストサイズ上限引き上げ（10MB）

### ⚠️ 進行中の項目

#### ふせいかい作成手順
- sessionStorageフラグ設定済み（`tutorial_step2_fuseikai_create`）
- 起動ロジック未実装
- チュートリアルステップ未実装

### ❌ 未実装の項目

#### もんだい作成手順
- チェックボックス作成
- 項目編集
- ボタン作成
- アルゴリズム新規作成遷移

#### アルゴリズム作成手順
- Blocklyブロック操作
- システム選択
- ブロック接続
- ブロックコピー
- 保存処理

#### テスト実行・保存手順
- テスト実行（2回）
- システム遷移検出
- 最終保存
- STEP2完了処理

---

## 各機能の詳細仕様

### sessionStorage管理

#### チュートリアルフラグ一覧

| フラグ名 | 設定場所 | 削除場所 | 用途 |
|---------|---------|---------|------|
| `tutorial_step2_start` | system_choice.html | system/index.html | STEP2開始 |
| `tutorial_step2_seikai_save` | system/index.html | system_create.html | せいかい保存画面起動 |
| `tutorial_step2_fuseikai_create` | system_create.html | system/index.html（未実装） | ふせいかい作成起動 |
| `tutorial_step2_fuseikai_save` | system/index.html（未実装） | system_create.html（未実装） | ふせいかい保存画面起動 |
| `tutorial_step2_mondai_create` | system_create.html（未実装） | system/index.html（未実装） | もんだい作成起動 |
| `tutorial_step2_algorithm_create` | system/index.html（未実装） | block.html（未実装） | アルゴリズム作成起動 |
| `tutorial_step2_algorithm_save` | block.html（未実装） | アルゴリズム保存画面（未実装） | アルゴリズム保存画面起動 |
| `tutorial_step2_test_execute` | アルゴリズム保存画面（未実装） | system/index.html（未実装） | テスト実行起動 |
| `tutorial_step2_mondai_save` | system/index.html（未実装） | system_create.html（未実装） | もんだい保存画面起動 |
| `tutorial_step2_complete` | system_create.html（未実装） | karihome.html（未実装） | STEP2完了 |

#### システムデータの保存・復元

| キー名 | 設定場所 | 削除場所 | 用途 |
|-------|---------|---------|------|
| `systemId` | system_list.html（編集時） | system_create.html（保存後） | システムID保存 |
| `systemName` | system_list.html（編集時） | system_create.html（保存後） | システム名保存 |
| `systemDescription` | system_list.html（編集時） | system_create.html（保存後） | システム詳細保存 |
| `systemDesignContent` | _history.html（保存ボタン時） | system_create.html（保存後） | 要素データJSON保存 |
| `returnFromCreate` | system_create.html（やめるボタン時） | _initialization.html（復元後） | 保存画面からの戻り検知 |
| `navigatingToCreate` | _history.html（保存ボタン時） | system_create.html（読み込み時） | 保存画面への遷移検知 |

### TutorialOverlayクラスAPI

#### コンストラクタ
```javascript
const tutorialOverlay = new TutorialOverlay();
```

#### メソッド

**init(steps, options)**
- チュートリアルを初期化
- パラメータ:
  - `steps`: ステップ配列
  - `options.onComplete`: 完了時のコールバック
  - `options.onSkip`: スキップ時のコールバック

**showStep(stepIndex)**
- 指定されたステップを表示
- パラメータ: `stepIndex` - ステップのインデックス（0始まり）

**next()**
- 次のステップへ進む
- ステップ数を超えたら`complete()`を呼び出し

**skip()**
- チュートリアルをスキップ
- 確認ダイアログ表示後、`onSkip`コールバックを呼び出し

**complete()**
- チュートリアルを完了
- `onComplete`コールバックを呼び出し後、`close()`

**close()**
- オーバーレイ、ハイライト、メッセージボックスを削除

**positionHighlight(element)**
- 指定要素をハイライト
- パラメータ: `element` - HTMLElement

**positionOverlayParts(element)**
- 指定要素を避けてオーバーレイを配置
- パラメータ: `element` - HTMLElement

**hideOverlay()** / **showOverlay()**
- オーバーレイの一時的な非表示/再表示

#### ステップオブジェクト仕様

```javascript
{
  target: '#elementId',           // ターゲット要素のCSSセレクタ（nullで画面中央）
  centerMessage: false,           // trueで強制的に画面中央表示
  message: 'メッセージ内容',        // HTML可、改行は<br>
  messagePosition: 'left',        // 'left', 'right', または未指定（自動）
  nextText: 'つぎへ',              // 次へボタンのテキスト（nullで非表示）
  showNextButton: true,           // 次へボタンを表示するか
  showSkip: true,                 // スキップボタンを表示するか
  requireClick: false,            // ターゲット要素のクリックを待機するか
  onShow: function() {},          // ステップ表示時のコールバック
  onNext: function() {}           // 次へ進む前のコールバック
}
```

### デバッグログ仕様

#### ログプレフィックス

| プレフィックス | 意味 | 用途 |
|-------------|------|------|
| 🔍 | 検索・確認 | 要素検索、フラグ確認 |
| ✅ | 成功 | 要素発見、処理完了 |
| ❌ | エラー | 要素未発見、処理失敗 |
| ⚠️ | 警告 | 想定外の状態 |
| 📋 | 情報 | ステップ情報、設定値 |
| 🎯 | フォーカス | ハイライト、ターゲット |
| 🎨 | スタイル | 色、サイズ変更 |
| 📝 | 入力 | テキスト入力、フォーム |
| 💾 | 保存 | 保存ボタン、データ保存 |
| 🔵 | 図形 | 円、三角など |
| 🔧 | イベント | イベントリスナー追加 |
| ➡️ | 進行 | 次のステップへ |
| 🎬 | コールバック | onShow、onNext実行 |

#### ログ出力箇所

1. **チュートリアル起動時**
   ```javascript
   console.log('🔍 tutorial_step2_start チェック:', shouldStartStep2);
   console.log('✅ STEP2チュートリアル開始準備');
   ```

2. **ステップ表示時**
   ```javascript
   console.log(`📍 showStep(${stepIndex}) called - steps.length: ${this.steps.length}`);
   console.log(`📋 ステップ ${stepIndex} の情報:`, {...});
   ```

3. **要素検出時**
   ```javascript
   console.log('🔍 ターゲット要素を検索: #elementId');
   console.log('✅ ターゲット要素が見つかりました:', element);
   ```

4. **操作検出時**
   ```javascript
   console.log('✅ 円が配置されました:', circle);
   console.log('✅ 編集パネルが開きました');
   console.log('✅ 適用ボタンが押されました');
   ```

---

## デバッグとトラブルシューティング

### よくある問題と解決方法

#### 問題1: チュートリアルが起動しない

**症状**
- sessionStorageフラグが設定されているのに起動しない
- コンソールにログが出力されない

**原因と解決**
1. **DOMContentLoadedのタイミング**
   - 原因: ページ読み込み後にスクリプトが実行される
   - 解決: `document.readyState`を確認して即座実行または遅延実行
   ```javascript
   if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', initTutorial);
   } else {
     setTimeout(initTutorial, 1000);
   }
   ```

2. **tutorialOverlayの未読み込み**
   - 原因: tutorial_overlay.jsが読み込まれる前に実行
   - 解決: `typeof tutorialOverlay === 'undefined'`でチェック

3. **要素の未存在**
   - 原因: ターゲット要素がDOM構築前
   - 解決: 要素存在確認後に起動、または再試行ロジック

#### 問題2: ステップが自動進行しない

**症状**
- 操作を完了してもステップが進まない
- メッセージが表示されたまま

**原因と解決**
1. **検出ロジックの未実行**
   - 原因: `onShow`コールバック内の検出処理が動作していない
   - 解決: デバッグログで検出処理の実行を確認
   ```javascript
   console.log('🔍 検出処理開始');
   const checkInterval = setInterval(() => {
     console.log('🔍 検出中...');
     // 検出処理
   }, 100);
   ```

2. **イベントリスナーの未追加**
   - 原因: ボタンなどのイベントリスナーが追加されていない
   - 解決: `dataset.tutorialListenerAdded`で重複チェック
   ```javascript
   if (!btn.dataset.tutorialListenerAdded) {
     btn.dataset.tutorialListenerAdded = 'true';
     btn.addEventListener('click', handler);
   }
   ```

3. **条件判定の誤り**
   - 原因: テキスト内容、要素数などの条件が合わない
   - 解決: 条件を緩和、または複数パターンに対応
   ```javascript
   if (value.includes('せいかい！') || 
       value.includes('せいかい!') || 
       value.includes('せいかい')) {
     // 進行
   }
   ```

#### 問題3: メッセージボックスの位置がおかしい

**症状**
- メッセージが画面外に表示される
- ターゲット要素と重なる

**原因と解決**
1. **位置計算のミス**
   - 原因: getBoundingClientRectの値が想定外
   - 解決: 画面内に収まるように調整
   ```javascript
   const viewportWidth = window.innerWidth;
   const viewportHeight = window.innerHeight;
   
   let left = rect.right + 20;
   if (left + messageRect.width > viewportWidth - 20) {
     left = rect.left - messageRect.width - 20;
   }
   ```

2. **messagePositionの指定**
   - 原因: 自動位置決定が不適切
   - 解決: `messagePosition: 'left'`などで強制指定

#### 問題4: 図形・画像が保存・復元されない

**症状**
- 図形や画像を作成しても保存後に消える
- リクエストサイズエラー

**原因と解決**
1. **収集処理の欠落**（✅ 修正済み）
   - 原因: collectCurrentElements()に図形・画像の処理がなかった
   - 解決: `.shape-element`、`.image-element`の収集処理を追加

2. **復元処理の欠落**（✅ 修正済み）
   - 原因: restoreSystemElements()のswitch文にケースがなかった
   - 解決: `restoreShape()`、`restoreImage()`関数を実装

3. **リクエストサイズ超過**（✅ 修正済み）
   - 原因: Base64画像データでリクエストが2.5MBを超えた
   - 解決: settings.pyで`DATA_UPLOAD_MAX_MEMORY_SIZE = 10MB`に設定

### デバッグ手順

1. **ブラウザ開発者ツールを開く**
   - F12キーまたは右クリック → 検証

2. **Consoleタブを確認**
   - ログプレフィックスで絞り込み（例: 🔍、✅、❌）
   - エラーメッセージの確認

3. **sessionStorageを確認**
   - Application → Storage → Session Storage
   - チュートリアルフラグの存在確認

4. **要素の存在確認**
   - Elements タブで DOM 構造を確認
   - ターゲット要素のID、クラス名を確認

5. **ネットワークタブで通信確認**
   - POSTリクエストのペイロードサイズ
   - レスポンスステータス

---

## 今後の作業項目

### 優先度: 高（必須実装）

#### 1. ふせいかい作成手順の実装
- [ ] system/index.htmlに起動ロジック追加
  - sessionStorage: `tutorial_step2_fuseikai_create`の検出
- [ ] チュートリアルステップの実装
  - 三角図形作成（青色、150px）
  - テキストボックス作成（「ふせいかい!」）
  - 保存ボタンクリック
- [ ] system_create.htmlにふせいかい保存チュートリアル追加
  - システム名入力検出（「ふせいかい」）
  - 保存ボタンクリック → `tutorial_step2_mondai_create`設定

#### 2. もんだい作成手順の実装
- [ ] system/index.htmlに起動ロジック追加
- [ ] チュートリアルステップの実装
  - チェックボックス作成（「1+1は?」、項目: 1,2,3）
  - ボタン作成
  - ボタン右クリック → アルゴリズム新規作成

#### 3. アルゴリズム作成手順の実装
- [ ] block.htmlに起動ロジック追加
- [ ] Blocklyブロック操作のチュートリアル実装
  - 「もしシステム〇〇の～」ブロック配置
  - システム選択（仮保存、1+1、項目:2）
  - 「システムを表示」ブロック配置（せいかい）
  - ブロックコピー（ふせいかい）
  - 保存処理

#### 4. テスト実行・保存手順の実装
- [ ] system/index.htmlにテスト実行チュートリアル追加
  - 実行ボタンクリック
  - チェックボックス操作
  - システム遷移検出
  - 保存処理
- [ ] system_create.htmlにもんだい保存チュートリアル追加
  - システム名・詳細入力検出
  - メイン画面へボタンクリック → `tutorial_step2_complete`設定

#### 5. STEP2完了処理の実装
- [ ] karihome.htmlに完了メッセージ追加
- [ ] サーバー側のSTEP2完了記録処理

### 優先度: 中（改善・最適化）

#### 1. ユーザビリティ向上
- [ ] メッセージの読みやすさ改善
  - フォントサイズ調整
  - 行間・余白の最適化
- [ ] アニメーション追加
  - ハイライトのパルス効果
  - メッセージボックスのフェードイン
- [ ] 音声ガイダンス（オプション）
  - 音声読み上げ機能

#### 2. エラーハンドリング強化
- [ ] タイムアウト処理
  - 一定時間操作がない場合のヒント表示
- [ ] リトライ機能
  - 要素検出失敗時の再試行
- [ ] エラーメッセージの改善
  - ユーザーフレンドリーなメッセージ

#### 3. パフォーマンス最適化
- [ ] ポーリング間隔の最適化
  - 100ms → 状況に応じて調整
- [ ] メモリリーク対策
  - setIntervalの適切なクリア
  - イベントリスナーの削除

### 優先度: 低（将来的な拡張）

#### 1. チュートリアルのカスタマイズ
- [ ] スキップ機能の改善
  - 特定ステップからの再開
- [ ] ヘルプボタン
  - 各ステップでの詳細説明表示

#### 2. 多言語対応
- [ ] 英語版チュートリアル
- [ ] 言語切り替え機能

#### 3. アナリティクス
- [ ] チュートリアル完了率の追跡
- [ ] つまづきポイントの分析

---

## 参考資料

### 主要ファイル一覧

| ファイルパス | 役割 |
|------------|------|
| `codemon/static/codemon/js/tutorial_overlay.js` | TutorialOverlayクラス |
| `codemon/static/codemon/css/tutorial_overlay.css` | チュートリアルスタイル |
| `accounts/templates/accounts/karihome.html` | ホーム画面（STEP1, STEP2完了） |
| `accounts/templates/system/system_choice.html` | システム選択画面 |
| `accounts/templates/system/index.html` | システム作成・編集画面（STEP2メイン） |
| `accounts/templates/system/system_create.html` | システム保存確認画面 |
| `accounts/templates/system/system_list.html` | システム一覧画面 |
| `accounts/templates/system/_history.html` | 履歴管理（保存ボタン） |
| `accounts/templates/system/_preview.html` | プレビュー（要素収集） |
| `accounts/templates/system/_initialization.html` | 初期化（要素復元） |
| `appproject/settings.py` | Django設定（リクエストサイズ制限） |

### sessionStorageフラグチートシート

```
tutorial_step2_start
  ↓ system/index.html
tutorial_step2_seikai_save
  ↓ system_create.html
tutorial_step2_fuseikai_create（未実装）
  ↓ system/index.html（未実装）
tutorial_step2_fuseikai_save（未実装）
  ↓ system_create.html（未実装）
tutorial_step2_mondai_create（未実装）
  ↓ system/index.html（未実装）
tutorial_step2_algorithm_create（未実装）
  ↓ block.html（未実装）
tutorial_step2_algorithm_save（未実装）
  ↓ アルゴリズム保存画面（未実装）
tutorial_step2_test_execute（未実装）
  ↓ system/index.html（未実装）
tutorial_step2_mondai_save（未実装）
  ↓ system_create.html（未実装）
tutorial_step2_complete（未実装）
  ↓ karihome.html（未実装）
```

---

## バージョン履歴

- **2026-02-05**: 初版作成
  - STEP2チュートリアルの設計と実装状況をまとめ
  - せいかい作成手順の完全実装
  - 図形・画像の保存・復元機能修正
  - リクエストサイズ上限引き上げ

---

## 連絡先・サポート

質問や不明点がある場合は、開発チームまでお問い合わせください。

このガイドは随時更新されます。最新版を確認してください。
