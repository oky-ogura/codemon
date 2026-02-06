/**
 * tutorial_seikai.js - せいかいチュートリアル
 * 
 * STEP2チュートリアルの最初のフェーズ
 * せいかい画面の作成方法を教える
 */

(function () {
    'use strict';

    /**
     * せいかいチュートリアルのステップ定義を返す
     */
    function getSeikaiiSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'それでは、じっさいに クイズシステムを つくって みましょう！<br><br>まずは 「せいかい」がめんを つくります。',
                nextText: 'つぎへ',
                onNext: null
            },
            {
                target: '#executeBtn',
                message: 'これは じっこうボタンだよ。<br>つくった システムを うごかすことが できるよ。<br><br>いまは まだ つかわないで OK！',
                nextText: 'わかった',
                onNext: null
            },
            {
                target: '#saveBtn',
                message: 'これは ほぞんボタンだよ。<br>つくった システムを ほぞんするときに つかうよ。',
                nextText: 'わかった',
                onNext: null
            },
            {
                target: null,
                centerMessage: true,
                message: 'それでは、せいかいがめんを つくりましょう！<br><br>まずは まるい かたちを えらびます。',
                nextText: 'つぎへ',
                onNext: null
            },
            {
                target: '#shapeBtn',
                message: 'この ずけい ボタンを クリックして、<br>メニューを ひらいてください！',
                messagePosition: 'left',
                requireClick: true,
                showSkip: true
            },
            {
                target: '#addCircleBtn',
                message: 'メニューから「えん」を クリックして ください！',
                requireClick: true,
                showSkip: true
            },
            {
                target: '.main-area',
                centerMessage: false,
                message: 'まるが がめんに でてきましたね！<br><br>つぎは、この まるを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。',
                messagePosition: 'left',
                nextText: null,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 円配置待機と右クリック待機');

                    try {
                        // 円が配置されるまで待つ（MutationObserver使用）
                        const circle = await tutorialHelper.waitForElement(
                            '[data-shape-type="circle"]',
                            5000
                        );

                        console.log('✅ 円が配置されました:', circle);
                        window.tutorialState.createdCircle = circle;

                        // 円をハイライト
                        tutorialOverlay.highlight.style.display = 'block';
                        tutorialOverlay.positionHighlight(circle);
                        tutorialOverlay.positionOverlayParts(circle);

                        // メッセージボックスを円の左側に表示
                        const circleRect = circle.getBoundingClientRect();
                        const messageBox = tutorialOverlay.messageBox;

                        messageBox.innerHTML = `
                            <div class="tutorial-step-indicator">
                                STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
                            </div>
                            <div class="tutorial-message-content">
                                まるが がめんに でてきましたね！<br><br>つぎは、この まるを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。
                            </div>
                            <div class="tutorial-buttons">
                                <button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>
                            </div>
                        `;

                        messageBox.style.display = 'block';
                        messageBox.style.left = `${Math.max(20, circleRect.left - 320)}px`;
                        messageBox.style.top = `${Math.max(20, circleRect.top)}px`;
                        messageBox.style.visibility = 'visible';

                        // 編集パネルの出現を待つ
                        await tutorialHelper.waitForElement('.shape-settings-panel', 10000);
                        console.log('✅ 編集パネルが開きました');
                        setTimeout(() => tutorialOverlay.next(), 300);

                    } catch (error) {
                        console.warn('⚠️ 円または編集パネルが見つかりませんでした:', error);
                        tutorialOverlay.next();
                    }
                }
            },
            {
                target: '.shape-settings-panel',
                centerMessage: false,
                message: 'すばらしい！<br><br>それでは、まるの「いろ」と「おおきさ」を かえましょう！<br><br><strong>【いろ】</strong><br>RGBで <strong>255, 0, 0</strong> と にゅうりょくするか、<br>カラーピッカーで <strong>あか</strong>を えらんでください。<br><br><strong>【おおきさ】</strong><br><strong>150</strong> に してください。<br><br>できたら、したの <strong>「てきよう」ボタン</strong>を おしてください！',
                messagePosition: 'left',
                nextText: null,
                showSkip: false,
                onShow: async function () {
                    console.log('🎨 色と大きさ変更開始');

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

                        // 適用ボタンのクリックを監視（非破壊的）
                        try {
                            const applyBtn = await tutorialHelper.waitForElement('#shapeApplyBtn', 5000);

                            tutorialHelper.monitorButtonClick(applyBtn, null, () => {
                                console.log('✅ 適用ボタンがクリックされました');
                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            });

                        } catch (error) {
                            console.warn('⚠️ 適用ボタンが見つかりませんでした');
                        }
                    }
                }
            },
            {
                target: '#formBtn',
                message: 'すばらしい！<br><br>つぎは もじを いれる はこを つくります。<br>この フォーム ボタンを クリックして ください！',
                messagePosition: 'left',
                requireClick: true,
                showSkip: true
            },
            {
                target: '#addTextBoxBtn',
                message: 'メニューから「テキストボックス」を クリックして ください！',
                messagePosition: 'left',
                requireClick: true,
                showSkip: true
            },
            {
                target: '.main-area',
                centerMessage: false,
                message: 'がめんを クリックして、<br>カーソルを うごかして、<br>テキストボックスを はいち してください！',
                messagePosition: 'left',
                nextText: null,
                showSkip: false,
                onShow: function () {
                    console.log('📝 テキストボックス配置開始');

                    const initialTextBoxCount = document.querySelectorAll('.text-box-container').length;
                    window.tutorialState.initialTextBoxCount = initialTextBoxCount;

                    // テキストボックス配置を監視
                    const checkTextBoxPlacement = setInterval(() => {
                        const textBoxes = document.querySelectorAll('.text-box-container');

                        if (textBoxes.length > initialTextBoxCount) {
                            clearInterval(checkTextBoxPlacement);
                            console.log('✅ テキストボックスが配置されました');

                            window.tutorialState.createdTextBox = textBoxes[textBoxes.length - 1];

                            setTimeout(() => {
                                tutorialOverlay.next();
                            }, 500);
                        }
                    }, 100);
                }
            },
            {
                target: '.text-box-container',
                centerMessage: false,
                message: 'テキストボックスが はいち できましたね！<br><br>このテキストボックスを クリックして、<br>「せいかい！」と にゅうりょく してください！',
                messagePosition: 'right',
                nextText: null,
                showSkip: false,
                onShow: function () {
                    console.log('✏️ テキスト入力開始');

                    const textBox = window.tutorialState.createdTextBox;

                    if (textBox) {
                        tutorialOverlay.positionHighlight(textBox);
                        tutorialOverlay.positionOverlayParts(textBox);

                        const rect = textBox.getBoundingClientRect();
                        const messageBox = tutorialOverlay.messageBox;

                        messageBox.innerHTML = `
                            <div class="tutorial-step-indicator">
                                STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
                            </div>
                            <div class="tutorial-message-content">
                                テキストボックスが はいち できましたね！<br><br>このテキストボックスを クリックして、<br>「せいかい！」と にゅうりょく してください！
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

                    // テキスト入力を監視
                    const checkTextInput = setInterval(() => {
                        const textAreas = document.querySelectorAll('.text-box');
                        let textCorrect = false;

                        textAreas.forEach(textArea => {
                            const value = textArea.value.trim();
                            if (value.includes('せいかい！') || value.includes('せいかい!') || value.includes('せいかい')) {
                                textCorrect = true;
                            }
                        });

                        if (textCorrect) {
                            clearInterval(checkTextInput);
                            console.log('✅ 正しいテキストが入力されました');

                            setTimeout(() => {
                                tutorialOverlay.next();
                            }, 500);
                        }
                    }, 100);
                }
            },
            {
                target: '#saveBtn',
                message: 'よくできました！<br><br>それでは、ほぞんボタンを おして、<br>「せいかい」という なまえで ほぞん してください！',
                nextText: 'わかった',
                showNextButton: false,
                onShow: async function () {
                    console.log('💾 保存ボタン説明');

                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) {
                        tutorialOverlay.positionHighlight(saveBtn);
                        tutorialOverlay.positionOverlayParts(saveBtn);

                        // 保存ボタンクリックを監視（非破壊的）
                        tutorialHelper.monitorButtonClick(saveBtn, null, () => {
                            console.log('✅ 保存ボタンがクリックされました');

                            // チュートリアルを終了
                            tutorialOverlay.close();

                            // 次のフェーズのフラグを設定
                            tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
                        });
                    }
                }
            }
        ];
    }

    // TutorialManagerに登録
    if (window.tutorialManager) {
        tutorialManager.register('seikai', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.START,
                forbidFlag: tutorialManager.FLAGS.SEIKAI_SAVE
            },
            steps: getSeikaiiSteps,
            onComplete: function () {
                console.log('🎉 せいかいチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
            },
            onSkip: function () {
                if (confirm('チュートリアルを とちゅうで やめますか？')) {
                    tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
                    return true;
                }
                return false;
            }
        });

        console.log('📝 せいかいチュートリアル登録完了');
    } else {
        console.error('❌ TutorialManagerが見つかりません');
    }

    // チュートリアル状態の初期化
    window.tutorialState = window.tutorialState || {
        isActive: false,
        waitingForColorChange: false,
        waitingForSizeChange: false,
        waitingForTextInput: false,
        targetColor: '#ff0000',
        targetSize: 150
    };

})();
