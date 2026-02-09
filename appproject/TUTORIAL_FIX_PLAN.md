# チュートリアル機能 修正計画

## 現状の問題
1. システム編集画面で`algorithm_advanced`チュートリアルが誤起動
2. せいかいチュートリアルの円配置ステップ（ブラウザキャッシュ問題）

## 修正内容（作業時間: 約30分）

### 修正1: algorithm_advancedにURL検証追加（5分）
**ファイル:** `tutorial_algorithm_advanced.js`

```javascript
trigger: {
    customCheck: function () {
        // アルゴリズム作成画面でのみ起動
        if (!window.location.href.includes('/algorithm/')) {
            console.log('⏭️ algorithm_advanced: URLが一致しません');
            return false;
        }
        
        const flag = sessionStorage.getItem('tutorial_mondai_to_algorithm');
        if (flag === 'true') {
            console.log('✅ アルゴリズムチュートリアル開始条件を満たしました');
            sessionStorage.removeItem('tutorial_mondai_to_algorithm');
            return true;
        }
        return false;
    }
}
```

### 修正2: seikaiチュートリアルの優先起動（10分）
**ファイル:** `tutorial_seikai.js`

```javascript
trigger: {
    priority: 100, // 最優先
    customCheck: function () {
        // システム編集画面でのみ起動
        if (!window.location.href.includes('/system/')) {
            return false;
        }
        
        // フラグなしでも起動（初回ユーザー対応）
        const completed = localStorage.getItem('tutorial_seikai_completed');
        if (completed === 'true') {
            return false; // 完了済みは起動しない
        }
        
        return true;
    }
}
```

### 修正3: tutorial_managerに優先順位機能追加（10分）
**ファイル:** `tutorial_manager.js`

```javascript
// チュートリアルを優先順位順にソート
checkTutorials() {
    const candidates = this.tutorials
        .filter(t => t.trigger.customCheck())
        .sort((a, b) => (b.trigger.priority || 0) - (a.trigger.priority || 0));
    
    if (candidates.length > 0) {
        this.start(candidates[0].name);
    }
}
```

### 修正4: ブラウザキャッシュクリア手順（ユーザー作業）
1. F12で開発者ツールを開く
2. 再読み込みボタンを右クリック
3. 「キャッシュの消去とハード再読み込み」を選択

## 検証手順
1. ✅ システム編集画面でseikaiチュートリアルが起動
2. ✅ アルゴリズム作成画面でalgorithm_advancedが起動
3. ✅ せいかいチュートリアルSTEP5（円配置→右クリック）が正常動作

## 所要時間
- コード修正: 25分
- テスト: 15分
- **合計: 40分**

## リスク評価
- **リスク: 低**
- **影響範囲: 限定的**（3ファイルのみ）
- **ロールバック: 容易**（git revert可能）

---

## 新規実装との比較

| 項目 | 既存修正 | 新規実装 |
|------|---------|----------|
| 作業時間 | 40分 | 12〜22時間 |
| リスク | 低 | 高 |
| 既存資産活用 | 100% | 30% |
| 技術的負債 | やや残る | なし |
| **推奨度** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 結論
**既存システムの修正を推奨します。**

理由:
1. 問題の本質は設計ではなく、フラグ管理の実装ミス
2. 40分で解決可能
3. 新規実装は投資対効果が低い
