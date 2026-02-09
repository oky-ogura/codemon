/**
 * チュートリアルオーバーレイシステム
 * 小学生向けのステップバイステップガイド
 */

class TutorialOverlay {
    constructor() {
        this.currentStep = 0;
        this.steps = [];
        this.onComplete = null;
        this.onSkip = null;
        this.overlayParts = null;
        this.highlight = null;
        this.messageBox = null;
        this.currentTargetElement = null;
        this.currentTargetOriginalStyles = null;
        this.progress = null; // 進捗追跡
    }

    /**
     * チュートリアルを初期化
     * @param {Array} steps - チュートリアルステップの配列
     * @param {Object} options - オプション設定
     */
    init(steps, options = {}) {
        this.steps = steps;
        this.onComplete = options.onComplete || null;
        this.onSkip = options.onSkip || null;
        this.currentStep = 0;

        // 進捗追跡を初期化（tutorialNameオプションがあれば）
        if (options.tutorialName) {
            this.progress = new TutorialProgress(options.tutorialName);
            console.log(`📊 進捗追跡を初期化: ${options.tutorialName}`);
        }

        // オーバーレイ要素を作成
        this.createOverlay();

        // 最初のステップを表示
        this.showStep(0);
    }

    /**
     * オーバーレイ要素を作成
     */
    createOverlay() {
        // 既存のオーバーレイがあれば削除
        if (this.overlay) {
            this.overlay.remove();
        }
        if (this.overlayParts) {
            this.overlayParts.forEach(part => part.remove());
        }

        // オーバーレイを4つの矩形に分割（上下左右）
        this.overlayParts = [];
        for (let i = 0; i < 4; i++) {
            const part = document.createElement('div');
            part.className = 'tutorial-overlay-part';
            document.body.appendChild(part);
            this.overlayParts.push(part);
        }

        // ハイライト枠
        this.highlight = document.createElement('div');
        this.highlight.className = 'tutorial-highlight';
        document.body.appendChild(this.highlight);

        // 左側固定パネル
        this.leftPanel = document.createElement('div');
        this.leftPanel.className = 'tutorial-left-panel';
        document.body.appendChild(this.leftPanel);

        // メッセージボックス（左側パネル内に配置）
        this.messageBox = document.createElement('div');
        this.messageBox.className = 'tutorial-message tutorial-message-fixed';
        this.leftPanel.appendChild(this.messageBox);

        // 左側パネルは固定位置なのでドラッグ不可
    }

    /**
     * 要素をドラッグ可能にする
     * @param {HTMLElement} element - ドラッグ可能にする要素
     */
    makeDraggable(element) {
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        const onMouseDown = (e) => {
            // メッセージ内容やボタンをクリックした場合はドラッグしない
            if (e.target.closest('.tutorial-btn') ||
                e.target.closest('.tutorial-message-content')) {
                return;
            }

            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;

            // 現在の位置を取得
            const rect = element.getBoundingClientRect();
            startLeft = rect.left;
            startTop = rect.top;

            element.style.cursor = 'grabbing';
            e.preventDefault();
        };

        const onMouseMove = (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            let newLeft = startLeft + deltaX;
            let newTop = startTop + deltaY;

            // 画面内に収める
            const rect = element.getBoundingClientRect();
            const maxLeft = window.innerWidth - rect.width;
            const maxTop = window.innerHeight - rect.height;

            newLeft = Math.max(0, Math.min(newLeft, maxLeft));
            newTop = Math.max(0, Math.min(newTop, maxTop));

            element.style.left = `${newLeft}px`;
            element.style.top = `${newTop}px`;
        };

        const onMouseUp = () => {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = 'grab';
            }
        };

        element.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        // カーソルスタイルを設定
        element.style.cursor = 'grab';
    }

    /**
     * 指定されたステップを表示
     * @param {number} stepIndex - ステップのインデックス
     */
    showStep(stepIndex) {
        console.log(`📍 showStep(${stepIndex}) called - steps.length: ${this.steps.length}`);

        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            console.log(`✅ チュートリアル完了 (stepIndex: ${stepIndex} >= ${this.steps.length})`);
            this.complete();
            return;
        }

        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];

        // 進捗を保存
        if (this.progress) {
            this.progress.save(stepIndex, {
                stepMessage: step.message ? step.message.substring(0, 100) : ''
            });
        }

        console.log(`📋 ステップ ${stepIndex} の情報:`, {
            target: step.target,
            message: step.message ? step.message.substring(0, 50) + '...' : 'なし',
            centerMessage: step.centerMessage,
            onShow: !!step.onShow
        });

        // 前のステップの表示を全てクリア
        this.clearCurrentDisplay();

        // targetがnullでcenterMessage: trueの場合は画面中央に大きく表示
        if ((!step.target && step.centerMessage !== false) || step.centerMessage === true) {
            console.log(`🎯 中央表示モード (target: ${step.target}, centerMessage: ${step.centerMessage})`);
            // 全画面オーバーレイを表示
            this.showFullOverlay();

            // ハイライトは非表示
            this.highlight.style.display = 'none';

            // メッセージボックスを画面中央に表示
            this.showCenterMessage(step);

            return;
        }

        // target: nullでcenterMessage: falseの場合、onShowで手動ハイライトを期待
        if (!step.target && step.centerMessage === false) {
            console.log(`🔧 手動ハイライトモード (target: null, centerMessage: false)`);
            // 全画面オーバーレイを表示（onShowで上書き可能）
            this.showFullOverlay();

            // ハイライトは一旦非表示（onShowで表示する）
            this.highlight.style.display = 'none';

            // onShowコールバックがあれば実行（ここでハイライトとメッセージを手動設定）
            if (step.onShow) {
                console.log(`🎬 onShow コールバックを実行します（手動モード）`);
                step.onShow();
            }

            return;
        }

        // ターゲット要素を取得
        console.log(`🔍 ターゲット要素を検索: ${step.target}`);

        // waitForElementを使用して堅牢に要素を取得
        this.waitForElement(step.target, {
            timeout: 10000,
            visible: true,
            clickable: step.requireClick || false,
            retryCount: 5
        }).then(targetElement => {
            console.log(`✅ ターゲット要素が見つかりました:`, targetElement);

            // 要素が画面内に表示されるようスクロール
            return this.ensureElementVisible(targetElement).then(() => targetElement);
        }).then(targetElement => {
            // ハイライトを配置
            this.positionHighlight(targetElement);

            // オーバーレイパーツを配置（ハイライト領域を避ける）
            this.positionOverlayParts(targetElement);

            // メッセージボックスを表示
            this.showMessage(step, targetElement);

            // onShowコールバックがあれば実行
            if (step.onShow) {
                console.log(`🎬 onShow コールバックを実行します`);
                step.onShow();
            }

            // ターゲット要素をクリック可能にする
            this.makeTargetClickable(targetElement, step);
        }).catch(error => {
            console.error(`❌ ターゲット要素の取得に失敗: ${step.target}`, error);

            // エラー時は次のステップへスキップするか確認
            const skipStep = confirm(
                `ターゲット要素が見つかりませんでした。\n` +
                `セレクタ: ${step.target}\n\n` +
                `このステップをスキップしますか？\n` +
                `（キャンセルでチュートリアルを終了します）`
            );

            if (skipStep) {
                console.log('⏭️ ステップをスキップします');
                this.next();
            } else {
                console.log('❌ チュートリアルを終了します');
                this.close();
            }
        });
    }

    /**
     * 現在の表示を全てクリア
     */
    clearCurrentDisplay() {
        // ハイライトを非表示
        if (this.highlight) {
            this.highlight.style.display = 'none';
        }

        // 左側パネルを非表示
        if (this.leftPanel) {
            this.leftPanel.style.display = 'none';
        }

        // メッセージボックスをクリア
        if (this.messageBox) {
            this.messageBox.innerHTML = '';
            this.messageBox.className = 'tutorial-message tutorial-message-fixed';
        }

        // オーバーレイパーツを非表示
        if (this.overlayParts) {
            this.overlayParts.forEach(part => {
                part.style.display = 'none';
            });
        }
    }

    /**
     * ハイライト枠を配置
     * @param {HTMLElement} element - ハイライトする要素
     */
    positionHighlight(element) {
        const rect = element.getBoundingClientRect();
        const padding = 10;

        this.highlight.style.top = `${rect.top - padding}px`;
        this.highlight.style.left = `${rect.left - padding}px`;
        this.highlight.style.width = `${rect.width + padding * 2}px`;
        this.highlight.style.height = `${rect.height + padding * 2}px`;
        this.highlight.style.display = 'block';
    }

    /**
     * オーバーレイパーツを配置（ハイライト領域を避ける）
     * @param {HTMLElement} element - ハイライトする要素
     */
    positionOverlayParts(element) {
        const rect = element.getBoundingClientRect();
        const padding = 10;

        // ハイライト領域
        const highlightTop = rect.top - padding;
        const highlightLeft = rect.left - padding;
        const highlightRight = rect.right + padding;
        const highlightBottom = rect.bottom + padding;

        // 上部のオーバーレイ
        this.overlayParts[0].style.top = '0';
        this.overlayParts[0].style.left = '0';
        this.overlayParts[0].style.width = '100%';
        this.overlayParts[0].style.height = `${highlightTop}px`;
        this.overlayParts[0].style.display = 'block';

        // 下部のオーバーレイ
        this.overlayParts[1].style.top = `${highlightBottom}px`;
        this.overlayParts[1].style.left = '0';
        this.overlayParts[1].style.width = '100%';
        this.overlayParts[1].style.height = `calc(100% - ${highlightBottom}px)`;
        this.overlayParts[1].style.display = 'block';

        // 左部のオーバーレイ
        this.overlayParts[2].style.top = `${highlightTop}px`;
        this.overlayParts[2].style.left = '0';
        this.overlayParts[2].style.width = `${highlightLeft}px`;
        this.overlayParts[2].style.height = `${highlightBottom - highlightTop}px`;
        this.overlayParts[2].style.display = 'block';

        // 右部のオーバーレイ
        this.overlayParts[3].style.top = `${highlightTop}px`;
        this.overlayParts[3].style.left = `${highlightRight}px`;
        this.overlayParts[3].style.width = `calc(100% - ${highlightRight}px)`;
        this.overlayParts[3].style.height = `${highlightBottom - highlightTop}px`;
        this.overlayParts[3].style.display = 'block';
    }

    /**
     * 全画面オーバーレイを表示（ハイライトなし）
     */
    showFullOverlay() {
        // 全画面を覆うオーバーレイを1つだけ表示
        this.overlayParts[0].style.top = '0';
        this.overlayParts[0].style.left = '0';
        this.overlayParts[0].style.width = '100%';
        this.overlayParts[0].style.height = '100%';
        this.overlayParts[0].style.display = 'block';

        // その他のパーツは非表示
        for (let i = 1; i < this.overlayParts.length; i++) {
            this.overlayParts[i].style.display = 'none';
        }
    }

    /**
     * 画面中央に大きくメッセージを表示（左側パネルに変更）
     * @param {Object} step - ステップ情報
     */
    showCenterMessage(step) {
        // nextTextのデフォルト値を設定
        const nextButtonText = step.nextText !== null && step.nextText !== undefined ? step.nextText : 'つぎへ';
        const showNextButton = !step.requireClick && step.nextText !== null;

        // メッセージ内容を構築
        this.messageBox.innerHTML = `
            <div class="tutorial-step-indicator">
                STEP ${this.currentStep + 1} / ${this.steps.length}
            </div>
            <div class="tutorial-message-content">
                ${step.message}
            </div>
            <div class="tutorial-buttons">
                ${step.showSkip !== false ? '<button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>' : ''}
                ${showNextButton ? `<button class="tutorial-btn tutorial-btn-next" onclick="tutorialOverlay.next()">${nextButtonText}</button>` : ''}
            </div>
        `;

        // 左側パネルを表示
        this.leftPanel.style.display = 'flex';
        this.messageBox.className = 'tutorial-message tutorial-message-fixed';
    }

    /**
     * メッセージボックスを表示（左側パネルに変更）
     * @param {Object} step - ステップ情報
     * @param {HTMLElement} targetElement - ターゲット要素
     */
    showMessage(step, targetElement) {
        // nextTextのデフォルト値を設定
        const nextButtonText = step.nextText !== null && step.nextText !== undefined ? step.nextText : 'つぎへ';
        const showNextButton = !step.requireClick && step.nextText !== null;

        // メッセージ内容を構築
        this.messageBox.innerHTML = `
            <div class="tutorial-step-indicator">
                STEP ${this.currentStep + 1} / ${this.steps.length}
            </div>
            <div class="tutorial-message-content">
                ${step.message}
            </div>
            <div class="tutorial-buttons">
                ${step.showSkip !== false ? '<button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>' : ''}
                ${showNextButton ? `<button class="tutorial-btn tutorial-btn-next" onclick="tutorialOverlay.next()">${nextButtonText}</button>` : ''}
            </div>
        `;

        // 左側パネルを表示
        this.leftPanel.style.display = 'flex';
        this.messageBox.className = 'tutorial-message tutorial-message-fixed';
    }

    /**
     * ターゲット要素をクリック可能にする
     * @param {HTMLElement} element - ターゲット要素
     * @param {Object} step - ステップ情報
     */
    makeTargetClickable(element, step) {
        // 元のスタイルを保存
        const originalZIndex = element.style.zIndex;
        const originalPosition = element.style.position;
        const originalPointerEvents = element.style.pointerEvents;

        // z-indexを高くして、オーバーレイより上に表示
        element.style.zIndex = '150004';
        element.style.pointerEvents = 'auto';

        // positionがstaticの場合のみrelativeにする（absolute/fixedの場合は変更しない）
        const computedStyle = window.getComputedStyle(element);
        if (computedStyle.position === 'static') {
            element.style.position = 'relative';
        }

        if (step.requireClick) {
            const clickHandler = () => {
                console.log('✅ ターゲット要素がクリックされました');
                element.removeEventListener('click', clickHandler);

                // 元のスタイルに戻す
                element.style.zIndex = originalZIndex;
                element.style.position = originalPosition;
                element.style.pointerEvents = originalPointerEvents;

                // onNextコールバックがあれば実行
                if (step.onNext) {
                    step.onNext();
                } else {
                    // onNextがない場合は自動で次へ
                    setTimeout(() => this.next(), 300);
                }
            };

            element.addEventListener('click', clickHandler);
        } else {
            // クリック不要の場合も次のステップ移動時に元に戻す
            this.currentTargetElement = element;
            this.currentTargetOriginalStyles = {
                zIndex: originalZIndex,
                position: originalPosition,
                pointerEvents: originalPointerEvents
            };
        }
    }

    /**
     * 次のステップへ進む
     */
    next() {
        console.log(`🔄 next() called - currentStep: ${this.currentStep}, total steps: ${this.steps.length}`);

        // 前のターゲット要素のスタイルを元に戻す
        if (this.currentTargetElement && this.currentTargetOriginalStyles) {
            this.currentTargetElement.style.zIndex = this.currentTargetOriginalStyles.zIndex;
            this.currentTargetElement.style.position = this.currentTargetOriginalStyles.position;
            this.currentTargetElement.style.pointerEvents = this.currentTargetOriginalStyles.pointerEvents;
        }

        console.log(`➡️ showStep(${this.currentStep + 1}) を呼び出します`);
        this.showStep(this.currentStep + 1);
        console.log(`✅ showStep 完了 - 新しい currentStep: ${this.currentStep}`);
    }

    /**
     * チュートリアルをスキップ
     */
    skip() {
        if (confirm('チュートリアルをとばしますか？\nあとからメイン画面のボタンで見ることができます。')) {
            if (this.onSkip) {
                this.onSkip();
            }
            this.close();
        }
    }

    /**
     * チュートリアル完了
     */
    complete() {
        // 進捗をクリア
        if (this.progress) {
            this.progress.clear();
        }

        if (this.onComplete) {
            this.onComplete();
        }
        this.close();
    }

    /**
     * チュートリアルを閉じる
     */
    close() {
        // 進捗をクリア（completeから呼ばれた場合は既にクリア済み）
        if (this.progress) {
            this.progress.clear();
        }

        // オーバーレイパーツを削除
        if (this.overlayParts) {
            this.overlayParts.forEach(part => {
                part.style.display = 'none';
                setTimeout(() => part.remove(), 300);
            });
        }

        // その他の要素を削除
        if (this.highlight) {
            this.highlight.style.display = 'none';
            setTimeout(() => this.highlight.remove(), 300);
        }

        if (this.messageBox) {
            this.messageBox.style.display = 'none';
            setTimeout(() => this.messageBox.remove(), 300);
        }
    }

    /**
     * オーバーレイを一時的に非表示にする（編集中など）
     */
    hideOverlay() {
        if (this.overlayParts) {
            this.overlayParts.forEach(part => {
                part.style.display = 'none';
            });
        }
        if (this.highlight) {
            this.highlight.style.display = 'none';
        }
        if (this.messageBox) {
            this.messageBox.style.display = 'none';
        }
    }

    /**
     * オーバーレイを再表示する
     */
    showOverlay() {
        if (this.overlayParts) {
            this.overlayParts.forEach(part => {
                part.style.display = 'block';
            });
        }
        if (this.highlight) {
            this.highlight.style.display = 'block';
        }
        if (this.messageBox) {
            this.messageBox.style.display = 'block';
        }
    }

    // ========================================
    // デバッグ機能
    // ========================================

    /**
     * デバッグモードを有効化
     */
    enableDebugMode() {
        this.debugMode = true;
        this.addDebugPanel();
        console.log('🐛 Tutorial Debug Mode ENABLED');
    }

    /**
     * デバッグパネルを追加
     */
    addDebugPanel() {
        // 既存のパネルがあれば削除
        const existing = document.getElementById('tutorial-debug-panel');
        if (existing) existing.remove();

        const panel = document.createElement('div');
        panel.id = 'tutorial-debug-panel';
        panel.innerHTML = `
            <style>
                #tutorial-debug-panel {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    z-index: 99999;
                    background: #1a1a1a;
                    color: #00ff00;
                    padding: 15px;
                    border: 3px solid #ff0000;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    max-width: 300px;
                    box-shadow: 0 4px 20px rgba(255, 0, 0, 0.5);
                }
                #tutorial-debug-panel h3 {
                    margin: 0 0 10px 0;
                    color: #ff0000;
                    font-size: 16px;
                }
                #tutorial-debug-panel button {
                    margin: 2px;
                    padding: 5px 10px;
                    background: #333;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 11px;
                }
                #tutorial-debug-panel button:hover {
                    background: #00ff00;
                    color: #000;
                }
                .debug-info {
                    margin: 5px 0;
                    padding: 5px;
                    background: #2a2a2a;
                    border-radius: 3px;
                }
            </style>
            <h3>🐛 Tutorial Debug</h3>
            <div class="debug-info">
                Step: <span id="debug-current-step">0</span> / <span id="debug-total-steps">0</span>
            </div>
            <div style="margin: 10px 0;">
                <button onclick="tutorialOverlay.jumpToStep(0)">Step 0</button>
                <button onclick="tutorialOverlay.jumpToStep(3)">Step 3</button>
                <button onclick="tutorialOverlay.jumpToStep(6)">Step 6</button>
                <button onclick="tutorialOverlay.jumpToStep(9)">Step 9</button>
            </div>
            <div style="margin: 10px 0;">
                <button onclick="tutorialOverlay.showFlags()">📋 Show Flags</button>
                <button onclick="tutorialOverlay.clearAllFlags()">🗑️ Clear All</button>
            </div>
            <div style="margin: 10px 0;">
                <button onclick="tutorialOverlay.closeDebugPanel()">❌ Close</button>
            </div>
        `;
        document.body.appendChild(panel);

        // ステップ情報を更新
        this.updateDebugPanel();
    }

    /**
     * デバッグパネルの情報を更新
     */
    updateDebugPanel() {
        const currentStepEl = document.getElementById('debug-current-step');
        const totalStepsEl = document.getElementById('debug-total-steps');
        if (currentStepEl) currentStepEl.textContent = this.currentStep;
        if (totalStepsEl) totalStepsEl.textContent = this.steps.length;
    }

    /**
     * 指定ステップにジャンプ
     */
    jumpToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            console.error(`❌ Invalid step index: ${stepIndex}`);
            return;
        }
        console.log(`🎯 Jumping to step ${stepIndex}`);
        this.currentStep = stepIndex;
        this.showStep(stepIndex);
        this.updateDebugPanel();
    }

    /**
     * 全てのチュートリアルフラグを表示
     */
    showFlags() {
        const flags = {};
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            if (key.startsWith('tutorial_')) {
                flags[key] = sessionStorage.getItem(key);
            }
        }
        console.log('📋 Tutorial Flags:');
        console.table(flags);

        // フラグがない場合
        if (Object.keys(flags).length === 0) {
            console.log('ℹ️ No tutorial flags found');
        }

        return flags;
    }

    /**
     * 全てのチュートリアルフラグをクリア
     */
    clearAllFlags() {
        const keys = [];
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            if (key.startsWith('tutorial_')) {
                keys.push(key);
            }
        }
        keys.forEach(key => sessionStorage.removeItem(key));
        console.log(`✅ Cleared ${keys.length} tutorial flags:`, keys);
        alert(`🗑️ ${keys.length}個のチュートリアルフラグをクリアしました`);
    }

    /**
     * デバッグパネルを閉じる
     */
    closeDebugPanel() {
        const panel = document.getElementById('tutorial-debug-panel');
        if (panel) panel.remove();
        this.debugMode = false;
        console.log('🐛 Tutorial Debug Mode DISABLED');
    }

    /**
     * 要素が見つかるまで待機（堅牢性向上）
     * @param {string} selector - CSSセレクタ
     * @param {Object} options - オプション設定
     * @returns {Promise<HTMLElement>}
     */
    waitForElement(selector, options = {}) {
        const {
            timeout = 5000,           // タイムアウト時間（ミリ秒）
            visible = true,           // 可視性チェック
            clickable = false,        // クリック可能性チェック
            validator = null,         // カスタム検証関数
            retryCount = 3,           // リトライ回数
            retryDelay = 500          // リトライ間隔（ミリ秒）
        } = options;

        return new Promise((resolve, reject) => {
            let attempts = 0;
            let timeoutId = null;

            const check = () => {
                const elements = document.querySelectorAll(selector);

                // 1. 要素の存在確認
                if (elements.length === 0) {
                    console.warn(`⚠️ 要素未発見: ${selector} (試行${attempts + 1}/${retryCount})`);
                    if (++attempts < retryCount) {
                        setTimeout(check, retryDelay);
                        return;
                    }
                    reject(new Error(`要素が見つかりません: ${selector}`));
                    return;
                }

                // 2. 複数マッチの警告
                if (elements.length > 1) {
                    console.warn(`⚠️ 複数要素マッチ: ${selector} (${elements.length}個) - 最初の要素を使用`);
                }

                const element = elements[0];

                // 3. 可視性チェック
                if (visible) {
                    const rect = element.getBoundingClientRect();
                    const style = window.getComputedStyle(element);
                    if (rect.width === 0 || rect.height === 0 ||
                        style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        console.warn(`⚠️ 要素が非表示: ${selector} (試行${attempts + 1}/${retryCount})`);
                        if (++attempts < retryCount) {
                            setTimeout(check, retryDelay);
                            return;
                        }
                        reject(new Error(`要素が非表示です: ${selector}`));
                        return;
                    }
                }

                // 4. クリック可能性チェック
                if (clickable) {
                    const rect = element.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const topElement = document.elementFromPoint(centerX, centerY);
                    if (!element.contains(topElement) && topElement !== element) {
                        console.warn(`⚠️ 要素がクリック不可（他要素に覆われている）: ${selector}`);
                        // クリック不可でもエラーにはせず警告のみ
                    }
                }

                // 5. カスタム検証
                if (validator && !validator(element)) {
                    console.warn(`⚠️ カスタム検証失敗: ${selector} (試行${attempts + 1}/${retryCount})`);
                    if (++attempts < retryCount) {
                        setTimeout(check, retryDelay);
                        return;
                    }
                    reject(new Error(`要素の検証に失敗しました: ${selector}`));
                    return;
                }

                console.log(`✅ 要素検証成功: ${selector}`);
                if (timeoutId) clearTimeout(timeoutId);
                resolve(element);
            };

            // 初回チェック開始
            check();

            // タイムアウト設定
            timeoutId = setTimeout(() => {
                reject(new Error(`タイムアウト（${timeout}ms）: ${selector}`));
            }, timeout);
        });
    }

    /**
     * 要素が画面内に表示されるようスクロール
     * @param {HTMLElement} element - スクロール対象の要素
     * @param {string} behavior - スクロール動作 ('smooth' | 'auto')
     * 
     * Note: scrollIntoViewを無効化しました。
     * fixed positionのチュートリアルパネルがスクロール時にずれる問題を回避するため、
     * 要素が画面外にあってもハイライトで強調表示するのみとします。
     */
    ensureElementVisible(element, behavior = 'smooth') {
        // スクロール処理を無効化
        console.log(`ℹ️ 要素の可視性チェック（スクロールなし）:`, element);
        return Promise.resolve();
    }

    /**
     * エラーハンドリング付きでステップを表示
     * @param {number} stepIndex - ステップインデックス
     */
    async showStepSafely(stepIndex) {
        try {
            await this.showStep(stepIndex);
        } catch (error) {
            console.error(`❌ ステップ${stepIndex}でエラー:`, error);

            // ユーザーに選択肢を提示
            const retry = confirm(
                `チュートリアルでエラーが発生しました。\n` +
                `エラー: ${error.message}\n\n` +
                `もう一度試しますか？\n` +
                `（キャンセルでチュートリアルを終了します）`
            );

            if (retry) {
                // リトライ（1秒待機）
                console.log('🔄 チュートリアルをリトライします...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                return this.showStepSafely(stepIndex);
            } else {
                // チュートリアル終了
                console.log('❌ ユーザーがチュートリアルを終了しました');
                this.close();
            }
        }
    }
}

// グローバルインスタンスを作成
window.tutorialOverlay = new TutorialOverlay();
console.log('🔧 TutorialOverlay loaded and attached to window');

/**
 * チュートリアル進捗追跡クラス
 */
class TutorialProgress {
    constructor(tutorialName) {
        this.key = `tutorial_progress_${tutorialName}`;
    }

    /**
     * 進捗を保存
     * @param {number} stepIndex - ステップインデックス
     * @param {Object} data - 追加データ
     */
    save(stepIndex, data = {}) {
        const progress = {
            step: stepIndex,
            timestamp: Date.now(),
            ...data
        };
        sessionStorage.setItem(this.key, JSON.stringify(progress));
        console.log(`💾 進捗保存: ${this.key} - Step ${stepIndex}`);
    }

    /**
     * 進捗を読み込み
     * @returns {Object|null}
     */
    load() {
        const data = sessionStorage.getItem(this.key);
        if (data) {
            try {
                return JSON.parse(data);
            } catch (e) {
                console.error('進捗データの読み込みエラー:', e);
                return null;
            }
        }
        return null;
    }

    /**
     * 進捗をクリア
     */
    clear() {
        sessionStorage.removeItem(this.key);
        console.log(`🗑️ 進捗クリア: ${this.key}`);
    }

    /**
     * チュートリアルを再開すべきか判定
     * @param {number} maxElapsedMinutes - 最大経過時間（分）
     * @returns {boolean}
     */
    shouldResume(maxElapsedMinutes = 30) {
        const progress = this.load();
        if (!progress) return false;

        // 指定時間以内なら再開
        const elapsed = Date.now() - progress.timestamp;
        const maxElapsed = maxElapsedMinutes * 60 * 1000;
        return elapsed < maxElapsed;
    }

    /**
     * 進捗情報を取得
     * @returns {Object|null}
     */
    getProgress() {
        return this.load();
    }
}

// TutorialProgressをグローバルに公開
window.TutorialProgress = TutorialProgress;

// デバッグ用：コンソールからアクセス可能なヘルパー
window.debugTutorial = function () {
    tutorialOverlay.enableDebugMode();
};

window.showTutorialFlags = function () {
    return tutorialOverlay.showFlags();
};

window.clearTutorialFlags = function () {
    tutorialOverlay.clearAllFlags();
};
