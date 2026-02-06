/**
 * tutorial_fuseikai.js - ふせいかいチュートリアル
 * 
 * STEP2チュートリアルの2番目のフェーズ
 * ふせいかい画面の作成方法を教える（三角形＋青色）
 */

(function () {
    'use strict';

    function getFuseikaiSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'つぎは「ふせいかい」がめんを つくりましょう！<br><br>こんどは さんかくと あおいろを つかいます。',
                nextText: 'つぎへ',
                onNext: null
            },
            {
                target: '#shapeBtn',
                message: 'まず、ずけいボタンを クリックして ください！',
                requireClick: true,
                onNext: function () {
                    const shapeBtn = document.getElementById('shapeBtn');
                    if (shapeBtn && (!shapeBtn.getAttribute('aria-expanded') || shapeBtn.getAttribute('aria-expanded') === 'false')) {
                        shapeBtn.click();
                    }
                    setTimeout(() => tutorialOverlay.next(), 300);
                }
            },
            {
                target: '#addTriangleBtn',
                message: 'メニューから「さんかく」を クリックして ください！',
                requireClick: true,
                onNext: async function () {
                    console.log('🔺 三角形ボタンがクリックされました');

                    try {
                        const triangle = await tutorialHelper.waitForElement('[data-shape-type="triangle"]', 5000);
                        console.log('✅ 三角形が配置されました:', triangle);
                        window.tutorialState.createdTriangle = triangle;
                        setTimeout(() => tutorialOverlay.next(), 500);
                    } catch (error) {
                        console.warn('⚠️ 三角形が見つかりませんでした');
                        tutorialOverlay.next();
                    }
                }
            },
            {
                target: null,
                centerMessage: false,
                message: 'さんかくが できました！<br><br>つぎは、いろを あおに かえましょう。<br>さんかくを <strong>みぎクリック</strong> してね！',
                nextText: null,
                showNextButton: false,
                onShow: async function () {
                    console.log('🔺 三角形フォーカス＆右クリック待機');

                    if (window.tutorialState.createdTriangle) {
                        tutorialOverlay.highlight.style.display = 'block';
                        tutorialOverlay.positionHighlight(window.tutorialState.createdTriangle);
                        tutorialOverlay.positionOverlayParts(window.tutorialState.createdTriangle);

                        const rect = window.tutorialState.createdTriangle.getBoundingClientRect();
                        const messageBox = tutorialOverlay.messageBox;

                        messageBox.innerHTML = `
                            <div class="tutorial-step-indicator">
                                STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
                            </div>
                            <div class="tutorial-message-content">
                                さんかくが できました！<br><br>つぎは、いろを あおに かえましょう。<br>さんかくを <strong>みぎクリック</strong> してね！
                            </div>
                            <div class="tutorial-buttons">
                                <button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>
                            </div>
                        `;

                        messageBox.style.display = 'block';
                        messageBox.style.left = `${Math.max(20, rect.right + 20)}px`;
                        messageBox.style.top = `${Math.max(20, rect.top)}px`;
                        messageBox.style.visibility = 'visible';
                    }

                    try {
                        await tutorialHelper.waitForElement('.shape-settings-panel', 10000);
                        console.log('✅ 編集パネルが開きました');
                        setTimeout(() => tutorialOverlay.next(), 300);
                    } catch (error) {
                        console.warn('⚠️ 編集パネルが見つかりませんでした');
                    }
                }
            },
            {
                target: '.shape-settings-panel',
                centerMessage: false,
                message: 'すばらしい！<br><br>それでは、さんかくの「いろ」を あおに かえましょう！<br><br><strong>【いろ】</strong><br>RGBで <strong>0, 0, 255</strong> と にゅうりょくするか、<br>カラーピッカーで <strong>あお</strong>を えらんでください。<br><br>できたら、したの <strong>「てきよう」ボタン</strong>を おしてください！',
                messagePosition: 'left',
                nextText: null,
                showSkip: false,
                onShow: async function () {
                    console.log('🎨 色変更開始（ふせいかい）');

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
                message: 'つぎは、もじを いれましょう！<br><br>フォームボタンを クリックして ください！',
                requireClick: true,
                onNext: function () {
                    const formBtn = document.getElementById('formBtn');
                    if (formBtn && (!formBtn.getAttribute('aria-expanded') || formBtn.getAttribute('aria-expanded') === 'false')) {
                        formBtn.click();
                    }
                    setTimeout(() => tutorialOverlay.next(), 300);
                }
            },
            {
                target: '#addTextBoxBtn',
                message: 'メニューから「テキストボックス」を クリックして ください！',
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
                    console.log('📝 テキストボックス配置開始（ふせいかい）');

                    const initialTextBoxCount = document.querySelectorAll('.text-box-container').length;
                    window.tutorialState.initialTextBoxCount = initialTextBoxCount;

                    const checkTextBoxPlacement = setInterval(() => {
                        const currentTextBoxes = document.querySelectorAll('.text-box-container');

                        if (currentTextBoxes.length > initialTextBoxCount) {
                            clearInterval(checkTextBoxPlacement);
                            console.log('✅ テキストボックスが配置されました');

                            window.tutorialState.createdTextBox = currentTextBoxes[currentTextBoxes.length - 1];

                            setTimeout(() => {
                                tutorialOverlay.next();
                            }, 500);
                        }
                    }, 300);
                }
            },
            {
                target: null,
                centerMessage: false,
                message: 'テキストボックスに<br>「ふせいかい！」と にゅうりょく してください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    console.log('✍️ テキストボックス編集（ふせいかい）');

                    if (window.tutorialState.createdTextBox) {
                        tutorialOverlay.highlight.style.display = 'block';
                        tutorialOverlay.positionHighlight(window.tutorialState.createdTextBox);
                        tutorialOverlay.positionOverlayParts(window.tutorialState.createdTextBox);

                        const rect = window.tutorialState.createdTextBox.getBoundingClientRect();
                        const messageBox = tutorialOverlay.messageBox;

                        messageBox.innerHTML = `
                            <div class="tutorial-step-indicator">
                                STEP ${tutorialOverlay.currentStep + 1} / ${tutorialOverlay.steps.length}
                            </div>
                            <div class="tutorial-message-content">
                                テキストボックスに<br>「ふせいかい！」と にゅうりょく してください！
                            </div>
                            <div class="tutorial-buttons">
                                <button class="tutorial-btn tutorial-btn-skip" onclick="tutorialOverlay.skip()">とばす</button>
                            </div>
                        `;

                        messageBox.style.display = 'block';
                        messageBox.style.left = `${Math.max(20, rect.right + 20)}px`;
                        messageBox.style.top = `${Math.max(20, rect.top)}px`;
                        messageBox.style.visibility = 'visible';
                    }

                    let progressTriggered = false;

                    const checkTextContent = () => {
                        if (progressTriggered) return;

                        const textBoxes = document.querySelectorAll('.text-box-container .text-box, .text-box-container textarea, .text-box-container .input-box');

                        for (let input of textBoxes) {
                            const content = input.value;

                            if (content.includes('ふせいかい！') || content.includes('ふせいかい')) {
                                console.log('✅ 「ふせいかい！」が入力されました');
                                progressTriggered = true;

                                textBoxes.forEach(inp => {
                                    inp.removeEventListener('input', checkTextContent);
                                });

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                                return true;
                            }
                        }
                        return false;
                    };

                    setTimeout(() => {
                        const textBoxes = document.querySelectorAll('.text-box-container .text-box, .text-box-container textarea, .text-box-container .input-box');
                        textBoxes.forEach(input => {
                            input.addEventListener('input', checkTextContent);
                        });
                    }, 500);

                    const intervalCheck = setInterval(() => {
                        if (progressTriggered) {
                            clearInterval(intervalCheck);
                            return;
                        }

                        const textBoxes = document.querySelectorAll('.text-box-container .text-box, .text-box-container textarea, .text-box-container .input-box');
                        for (let input of textBoxes) {
                            const content = input.value;

                            if (content.includes('ふせいかい！') || content.includes('ふせいかい')) {
                                progressTriggered = true;
                                clearInterval(intervalCheck);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                                break;
                            }
                        }
                    }, 500);
                }
            },
            {
                target: '#saveBtn',
                message: 'よくできました！<br><br>ほぞんボタンを おして、<br>「ふせいかい」という なまえで ほぞん してください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    console.log('💾 保存ボタン説明（ふせいかい）');

                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) {
                        tutorialOverlay.positionHighlight(saveBtn);
                        tutorialOverlay.positionOverlayParts(saveBtn);

                        tutorialHelper.monitorButtonClick(saveBtn, null, () => {
                            console.log('✅ 保存ボタンがクリックされました（ふせいかい）');

                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('fuseikai', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.FUSEIKAI_CREATE,
                forbidFlag: tutorialManager.FLAGS.FUSEIKAI_SAVE
            },
            steps: getFuseikaiSteps,
            onComplete: function () {
                console.log('🎉 ふせいかいチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
            },
            onSkip: function () {
                if (confirm('チュートリアルを とちゅうで やめますか？')) {
                    tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                    return true;
                }
                return false;
            }
        });

        console.log('📝 ふせいかいチュートリアル登録完了');
    }

    window.tutorialState = window.tutorialState || {
        isActive: false,
        waitingForColorChange: false,
        targetColor: '#0000ff'
    };

})();
