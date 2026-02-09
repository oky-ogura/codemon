/**
 * 非破壊的イベントリスナーパターンの実装例
 * 
 * このファイルは、チュートリアルで既存機能を壊さないための
 * ベストプラクティスを示します。
 */

// ========================================
// パターン1: TutorialHelperを使用した安全なイベント監視
// ========================================

// ❌ 悪い例: preventDefaultで既存の動作を止めてしまう
function badPattern_blockingSave() {
    const saveBtn = document.querySelector('#save-btn');

    saveBtn.addEventListener('click', (e) => {
        e.preventDefault();  // ⚠️ 既存の保存処理が動かなくなる！
        tutorialOverlay.next();
    });
}

// ✅ 良い例: 既存の動作を妨げず監視
function goodPattern_monitoringSave() {
    const saveBtn = document.querySelector('#save-btn');

    // preventDefaultしない、capture: trueで先に検出
    const listenerInfo = tutorialHelper.addSafeEventListener(
        saveBtn,
        'click',
        (e) => {
            console.log('💾 保存ボタンがクリックされました（チュートリアル検出）');
            // 既存の動作はそのまま進む

            // チュートリアルの次のステップへ
            setTimeout(() => {
                tutorialOverlay.next();
            }, 100);
        },
        { capture: true }  // 既存リスナーより先に実行
    );

    // チュートリアル終了時に削除
    tutorialOverlay.onComplete = () => {
        tutorialHelper.removeSafeEventListener(listenerInfo);
    };
}

// ========================================
// パターン2: monitorButtonClickヘルパーを使用
// ========================================

function goodPattern_usingHelper() {
    const saveBtn = document.querySelector('#save-btn');

    const listenerInfo = tutorialHelper.monitorButtonClick(
        saveBtn,

        // クリック前の処理（既存の動作は止めない）
        (event) => {
            console.log('📝 保存ボタンがクリックされようとしています');
        },

        // クリック後の処理
        (event) => {
            console.log('✅ 保存処理が実行されました');
            tutorialOverlay.next();
        }
    );
}

// ========================================
// パターン3: MutationObserverで要素の出現を待つ
// ========================================

// ❌ 悪い例: setIntervalで無限ループ
function badPattern_pollingForElement() {
    const checkInterval = setInterval(() => {
        const panel = document.querySelector('.edit-panel');
        if (panel) {
            clearInterval(checkInterval);
            // 処理...
        }
    }, 100);  // ⚠️ メモリリーク、パフォーマンス悪化
}

// ✅ 良い例: MutationObserverで効率的に監視
async function goodPattern_waitForElement() {
    try {
        // 要素が出現するまで待つ（Promise）
        const panel = await tutorialHelper.waitForElement('.edit-panel', 3000);
        console.log('✅ 編集パネルが出現しました', panel);

        // パネルが出現したら次のステップへ
        tutorialOverlay.next();

    } catch (error) {
        console.error('⏱️ タイムアウト: 編集パネルが見つかりませんでした');
    }
}

// ========================================
// パターン4: 既存のチュートリアルコードの改善例
// ========================================

// BEFORE: せいかいチュートリアルの適用ボタン監視（現在の実装）
function beforePattern_applyButton() {
    const checkApplyButton = setInterval(() => {
        const applyBtn = document.getElementById('shapeApplyBtn');

        if (applyBtn && !applyBtn.dataset.tutorialListenerAdded) {
            applyBtn.dataset.tutorialListenerAdded = 'true';

            const handler = function (e) {
                clearInterval(checkApplyButton);
                applyBtn.removeEventListener('click', handler);
                delete applyBtn.dataset.tutorialListenerAdded;

                setTimeout(() => {
                    tutorialOverlay.next();
                }, 500);
            };

            applyBtn.addEventListener('click', handler);
        }
    }, 100);
}

// AFTER: TutorialHelperを使った改善版
async function afterPattern_applyButton() {
    try {
        // 要素の出現を効率的に待つ
        const applyBtn = await tutorialHelper.waitForElement('#shapeApplyBtn', 5000);

        // 非破壊的にクリックを監視
        const listenerInfo = tutorialHelper.monitorButtonClick(
            applyBtn,
            null,  // クリック前の処理は不要
            () => {
                // クリック後、パネルが閉じるのを待つ
                setTimeout(() => {
                    tutorialOverlay.next();
                }, 500);
            }
        );

        console.log('🔧 適用ボタンの監視を開始');

    } catch (error) {
        console.error('❌ 適用ボタンが見つかりませんでした', error);
    }
}

// ========================================
// パターン5: チュートリアル終了時のクリーンアップ
// ========================================

function setupTutorialWithCleanup() {
    const steps = [
        // ... ステップ定義
    ];

    tutorialOverlay.init(steps, {
        onComplete: () => {
            console.log('🎉 チュートリアル完了');

            // 全てのイベントリスナーとオブザーバーを削除
            tutorialHelper.cleanup();

            // フラグを設定
            sessionStorage.setItem('tutorial_completed', 'true');
        },

        onSkip: () => {
            console.log('⏭️ チュートリアルスキップ');

            // スキップ時もクリーンアップ
            tutorialHelper.cleanup();

            return true;
        }
    });
}

// ========================================
// パターン6: 複数の要素を同時に監視
// ========================================

function goodPattern_multipleButtons() {
    const buttons = [
        { selector: '#save-btn', name: '保存' },
        { selector: '#delete-btn', name: '削除' },
        { selector: '#edit-btn', name: '編集' }
    ];

    buttons.forEach(({ selector, name }) => {
        const btn = document.querySelector(selector);
        if (btn) {
            tutorialHelper.monitorButtonClick(btn, null, () => {
                console.log(`✅ ${name}ボタンがクリックされました`);
            });
        }
    });

    // チュートリアル終了時に一括削除
    tutorialOverlay.onComplete = () => {
        tutorialHelper.cleanup();
    };
}

// ========================================
// 使用例: せいかいチュートリアル（改善版）
// ========================================

async function improvedSeikaiiTutorial() {
    const steps = [
        // ... 他のステップ

        {
            target: '#shapeBtn',
            message: '図形を追加しましょう！',
            onNext: async function () {
                console.log('🎨 図形編集パネルを待機中...');

                // 編集パネルが出現するまで待つ
                const editPanel = await tutorialHelper.waitForElement('.edit-panel', 5000);
                console.log('✅ 編集パネルが出現しました');

                // 適用ボタンの出現を待つ
                const applyBtn = await tutorialHelper.waitForElement('#shapeApplyBtn', 5000);

                // 適用ボタンのクリックを監視
                tutorialHelper.monitorButtonClick(applyBtn, null, () => {
                    setTimeout(() => {
                        tutorialOverlay.next();
                    }, 500);
                });
            }
        },

        // ... 他のステップ
    ];

    tutorialOverlay.init(steps, {
        onComplete: () => {
            tutorialHelper.cleanup();
            sessionStorage.setItem('tutorial_seikai_completed', 'true');
        },
        onSkip: () => {
            tutorialHelper.cleanup();
            return true;
        }
    });
}

// ========================================
// まとめ: ベストプラクティス
// ========================================

/**
 * ✅ やるべきこと:
 * 
 * 1. TutorialHelperを使って非破壊的にイベントを監視
 * 2. MutationObserverで要素の出現を効率的に検出
 * 3. チュートリアル終了時に必ずcleanup()を呼ぶ
 * 4. capture: true でチュートリアルを先に実行（ただしpreventDefaultしない）
 * 5. Promise/async-awaitで非同期処理を明確に
 * 
 * ❌ やってはいけないこと:
 * 
 * 1. preventDefault()で既存の動作を止める
 * 2. setIntervalで無限ループ（cleanup忘れ）
 * 3. イベントリスナーの削除忘れ（メモリリーク）
 * 4. 既存のイベントリスナーを上書き
 * 5. グローバルな状態を直接変更
 */

console.log('📚 Non-destructive event patterns loaded');
