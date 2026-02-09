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
                target: '#shapeBtn',
                message: 'それでは、せいかいがめんを つくりましょう！<br><br>まずは まるい かたちを えらびます。<br><br>この ずけい ボタンを クリックして、<br>メニューを ひらいてください！',
                messagePosition: 'left',
                requireClick: true,
                showSkip: true
            },
            /* {
                target: '#shapeBtn',
                message: 'この ずけい ボタンを クリックして、<br>メニューを ひらいてください！',
                messagePosition: 'left',
                requireClick: true,
                showSkip: true
            }, */
            {
                target: '#addCircleBtn',
                message: 'メニューから「えん」を クリックして ください！',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: false,
                message: 'まるが がめんに でてきましたね！<br><br>つぎは、この まるを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。',
                messagePosition: 'left',
                nextText: null,
                showSkip: true,
                requireClick: false,
                showNextButton: false,
                onShow: async function () {
                    console.log('🎯 円配置待機と右クリック待機');

                    let circle;
                    try {
                        // 円が配置されるまで待つ（MutationObserver使用）
                        circle = await tutorialHelper.waitForElement(
                            '[data-shape-type="circle"]',
                            5000
                        );
                        console.log('✅ 円が配置されました:', circle);
                    } catch (error) {
                        console.warn('⚠️ 円が見つかりませんでした:', error);
                        const retry = confirm('円が見つかりませんでした。\nこのステップをスキップしますか？');
                        if (retry) {
                            tutorialOverlay.next();
                        }
                        return; // エラー時は処理を中断
                    }

                    // 円が見つかったので、ハイライトとメッセージを表示
                    window.tutorialState.createdCircle = circle;

                    try {
                        // 円をハイライト
                        tutorialOverlay.highlight(circle);
                        console.log('✅ 円をハイライトしました');

                        // 左側パネルでメッセージを表示
                        const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                        tutorialOverlay.showMessage(step, circle);
                        console.log('✅ メッセージを表示しました');
                    } catch (displayError) {
                        console.error('❌ ハイライト/メッセージ表示エラー:', displayError);
                    }

                    // 円の右クリックを待つ（next()はこのリスナー内でのみ呼ばれる）
                    circle.addEventListener('contextmenu', async function onRightClick(e) {
                        console.log('✅ 円が右クリックされました');

                        // 編集パネルの出現を待つ
                        try {
                            await tutorialHelper.waitForElement('.shape-settings-panel', 3000);
                            console.log('✅ 編集パネルが開きました');
                            setTimeout(() => tutorialOverlay.next(), 300);
                        } catch (panelError) {
                            console.warn('⚠️ 編集パネルが見つかりませんでした:', panelError);
                            // パネルが見つからなくても次に進む
                            setTimeout(() => tutorialOverlay.next(), 300);
                        }
                    }, { once: true });

                    console.log('✅ 右クリックイベントリスナーを登録しました - ユーザーの右クリックを待機中...');
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
                        // 左側パネルでメッセージを表示
                        const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                        tutorialOverlay.showMessage(step, panel);
                        tutorialOverlay.highlight(panel);

                        // 進行管理
                        let isProceeding = false;
                        const proceedNext = () => {
                            if (isProceeding) return;
                            isProceeding = true;
                            setTimeout(() => { tutorialOverlay.next(); }, 500);
                        };

                        // パネル消失監視 (バックアップ)
                        const checkPanelRemoval = setInterval(() => {
                            if (!document.body.contains(panel)) {
                                clearInterval(checkPanelRemoval);
                                console.log('✅ パネル消失を検知');
                                proceedNext();
                            }
                        }, 200);

                        // 適用ボタンのクリックを監視
                        try {
                            const applyBtn = await tutorialHelper.waitForElement('#shapeApplyBtn', 5000);

                            tutorialHelper.monitorButtonClick(applyBtn, null, () => {
                                console.log('✅ 適用ボタンがクリックされました');
                                clearInterval(checkPanelRemoval);
                                proceedNext();
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
