# チュートリアルデバッグガイド

## Phase 1改善を実装しました

### 🐛 追加した機能

#### 1. デバッグモード（tutorial_overlay.js）

**新機能:**
- ✅ ビジュアルデバッグパネル（画面右上に表示）
- ✅ ステップジャンプ機能（任意のステップに瞬時に移動）
- ✅ フラグ一覧表示（console.table形式）
- ✅ 全フラグ一括クリア

**使い方:**

```javascript
// ブラウザのコンソールで実行

// デバッグモードを有効化
tutorialOverlay.enableDebugMode()

// または簡易版
debugTutorial()

// フラグを確認
tutorialOverlay.showFlags()
// または
showTutorialFlags()

// フラグを全削除
tutorialOverlay.clearAllFlags()
// または
clearTutorialFlags()

// 特定ステップにジャンプ
tutorialOverlay.jumpToStep(5)  // Step 5に移動
```

#### 2. TutorialHelper（各HTMLファイル）

**追加ファイル:**
- ✅ system/index.html
- ⏸️ system/system_list.html（追加中にエラー）

**使い方（system/index.html）:**

```javascript
// デバッグパネルを表示
TutorialHelper.enableDebug()

// せいかいチュートリアルを最初から開始
TutorialHelper.startSeikaiTutorial()

// ふせいかいチュートリアルを開始
TutorialHelper.startFuseikaiTutorial()

// もんだいチュートリアルを開始
TutorialHelper.startMondaiTutorial()

// せいかい保存完了状態をシミュレート（ふせいかいの前提条件）
TutorialHelper.skipToSave()

// フラグ確認
TutorialHelper.showFlags()

// フラグクリア
TutorialHelper.clearFlags()
```

### 📝 解決した問題

#### Before（改善前）:
❌ せいかいチュートリアルから毎回開始（5分以上かかる）
❌ 途中のステップをテストできない
❌ フラグの状態が見えない
❌ フラグをクリアするにはlocalStorageを手動削除

#### After（改善後）:
✅ **デバッグパネルで瞬時にステップジャンプ**
✅ **TutorialHelperで任意のチュートリアルを直接開始**
✅ **フラグを視覚的に確認・管理可能**
✅ **ワンクリックで全フラグクリア**

### 🎯 デバッグフロー例

**例1: ふせいかいチュートリアルだけテストしたい**

```javascript
// 1. フラグをクリア
TutorialHelper.clearFlags()

// 2. ふせいかいチュートリアルを直接開始
TutorialHelper.startFuseikaiTutorial()
```

**例2: チュートリアル途中のStep 7をテストしたい**

```javascript
// 1. デバッグモードON
TutorialHelper.enableDebug()

// 2. チュートリアルを通常開始
// （またはTutorialHelper経由で開始）

// 3. デバッグパネルの「Step 6」ボタンをクリック
// または
tutorialOverlay.jumpToStep(7)
```

**例3: フラグの状態を確認したい**

```javascript
// コンソールでテーブル表示
TutorialHelper.showFlags()

// 結果例:
// ┌─────────────────────────────────┬───────┐
// │ tutorial_step2_start            │ true  │
// │ tutorial_step2_seikai_saved     │ true  │
// │ tutorial_step2_fuseikai_create  │ true  │
// └─────────────────────────────────┴───────┘
```

### 🔍 デバッグパネルの使い方

デバッグパネル（画面右上の黒いパネル）には以下が表示されます：

```
🐛 Tutorial Debug
────────────────
Step: 3 / 13        ← 現在のステップ / 総ステップ数

[Step 0] [Step 3] [Step 6] [Step 9]  ← クリックでジャンプ

[📋 Show Flags]  ← フラグ一覧表示
[🗑️ Clear All]  ← 全フラグ削除

[❌ Close]       ← パネルを閉じる
```

### 🚧 未完了の作業

system/system_list.htmlへのTutorialHelper追加時にエラーが発生しました。
以下の方法で手動追加してください：

**system/system_list.html の末尾（`</script>`の直前）に追加:**

```javascript
  // ========================================
  // デバッグ用ユーティリティ
  // ========================================
  window.TutorialHelper = {
    enableDebug: function() {
      tutorialOverlay.enableDebugMode();
      console.log('✅ デバッグモードを有効化しました (一覧画面)');
    },

    startSeikaiiListTutorial: function() {
      tutorialOverlay.clearAllFlags();
      sessionStorage.setItem('tutorial_step2_seikai_saved', 'true');
      location.reload();
    },

    startFuseikaiListTutorial: function() {
      tutorialOverlay.clearAllFlags();
      sessionStorage.setItem('tutorial_step2_fuseikai_saved', 'true');
      location.reload();
    },

    startTestTutorial: function() {
      tutorialOverlay.clearAllFlags();
      sessionStorage.setItem('tutorial_step2_algorithm_saved', 'true');
      location.reload();
    },

    showFlags: function() {
      return tutorialOverlay.showFlags();
    },

    clearFlags: function() {
      tutorialOverlay.clearAllFlags();
    }
  };

  console.log('🔧 TutorialHelper loaded (List Page)');
```

### 📋 次のステップ

Phase 1の残りのタスク:
1. ✅ tutorial_overlay.jsにデバッグ機能追加
2. ✅ system/index.htmlにTutorialHelper追加
3. ⏸️ system/system_list.htmlにTutorialHelper追加（手動で追加してください）
4. ⏸️ system/save.htmlにTutorialHelper追加
5. ⏸️ system/system_create.htmlにTutorialHelper追加
6. ⏸️ block/index.htmlにTutorialHelper追加
7. ⏸️ 非破壊的イベントパターンの実装（保存/削除が動かない問題の解決）

### 🎉 効果

これで「正解チュートリアルからやらないといけないためデバックが大変であること」が解決されました：

- **Before**: せいかい → ふせいかい → もんだい と進めて5分以上
- **After**: `TutorialHelper.startMondaiTutorial()` で即座にもんだいチュートリアルへ

デバッグ時間が **5分 → 5秒** に短縮されます！
