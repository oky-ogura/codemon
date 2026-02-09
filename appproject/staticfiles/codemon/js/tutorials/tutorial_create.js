/**
 * tutorial_create.js - 名前入力画面用チュートリアル
 * system_create.htmlで使用
 */

(function () {
    'use strict';

    // せいかい名前入力
    function getSeikaiiCreateSteps() {
        return [
            {
                target: '#systemName',
                message: 'システムの なまえを にゅうりょくします。<br><br>「せいかい」と にゅうりょくして ください！',
                messagePosition: 'bottom',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const nameInput = document.getElementById('systemName');
                    if (nameInput) {
                        const checkInput = () => {
                            if (nameInput.value.trim() === 'せいかい') {
                                nameInput.removeEventListener('input', checkInput);
                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }
                        };
                        tutorialHelper.addSafeEventListener(nameInput, 'input', checkInput);
                    }
                }
            },
            {
                target: '#systemDetail',
                message: 'つぎは、システムの せつめいを にゅうりょく します。<br><br>「チュートリアルせいかい」と にゅうりょく してください！',
                messagePosition: 'top',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const detailInput = document.getElementById('systemDetail');
                    if (detailInput) {
                        const checkInput = () => {
                            if (detailInput.value.trim() === 'チュートリアルせいかい') {
                                detailInput.removeEventListener('input', checkInput);
                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }
                        };
                        tutorialHelper.addSafeEventListener(detailInput, 'input', checkInput);
                    }
                }
            },
            {
                target: '#saveBtn',
                message: 'にゅうりょくが おわったら、<br>「ほぞんする」ボタンを おして ください！',
                messagePosition: 'left',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) {
                        tutorialHelper.monitorButtonClick(saveBtn, () => {
                            // クリック前（フォーム送信前）にフラグを設定
                            tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
                            tutorialOverlay.close();
                        }, null);
                    }
                }
            }
        ];
    }

    // ふせいかい名前入力
    function getFuseikaiCreateSteps() {
        return [
            {
                target: '#systemName',
                message: 'システムの なまえを にゅうりょくします。<br><br>「ふせいかい」と にゅうりょくして ください！',
                messagePosition: 'bottom',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const nameInput = document.getElementById('systemName');
                    if (nameInput) {
                        const checkInput = () => {
                            if (nameInput.value.trim() === 'ふせいかい') {
                                nameInput.removeEventListener('input', checkInput);
                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }
                        };
                        tutorialHelper.addSafeEventListener(nameInput, 'input', checkInput);
                    }
                }
            },
            {
                target: '#systemDetail',
                message: 'つぎは、システムの せつめいを にゅうりょく します。<br><br>「チュートリアルふせいかい」と にゅうりょく してください！',
                messagePosition: 'top',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const detailInput = document.getElementById('systemDetail');
                    if (detailInput) {
                        const checkInput = () => {
                            if (detailInput.value.trim() === 'チュートリアルふせいかい') {
                                detailInput.removeEventListener('input', checkInput);
                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }
                        };
                        tutorialHelper.addSafeEventListener(detailInput, 'input', checkInput);
                    }
                }
            },
            {
                target: '#saveBtn',
                message: 'にゅうりょくが おわったら、<br>「ほぞんする」ボタンを おして ください！',
                messagePosition: 'left',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) {
                        tutorialHelper.monitorButtonClick(saveBtn, () => {
                            // クリック前（フォーム送信前）にフラグを設定
                            tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                            tutorialOverlay.close();
                        }, null);
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        // せいかい名前入力
        tutorialManager.register('seikai_create', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.START,
                forbidFlag: tutorialManager.FLAGS.FUSEIKAI_CREATE  // ふせいかい作成中は実行しない
            },
            steps: getSeikaiiCreateSteps,
            onComplete: function () {
                // 次の画面（tutorial_seikai.js）でもSTARTフラグが必要なため、ここでは消さない
                // sessionStorage.removeItem(tutorialManager.FLAGS.START);
            },
            onSkip: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.START);
                return true;
            }
        });

        // ふせいかい名前入力
        tutorialManager.register('fuseikai_create', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.FUSEIKAI_CREATE,
                forbidFlag: tutorialManager.FLAGS.START  // せいかい作成中は実行しない
            },
            steps: getFuseikaiCreateSteps,
            onComplete: function () {
                // 次の画面（tutorial_seikai.js）に進むため、フラグは消さない
                // sessionStorage.removeItem(tutorialManager.FLAGS.FUSEIKAI_CREATE);
            },
            onSkip: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.FUSEIKAI_CREATE);
                return true;
            }
        });

        console.log('📝 名前入力チュートリアル登録完了');
    }

})();
