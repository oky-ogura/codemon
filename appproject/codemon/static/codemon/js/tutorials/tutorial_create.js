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
                target: null,
                centerMessage: true,
                message: 'システムの なまえを にゅうりょくします。<br><br>「せいかい」と にゅうりょくして、<br>「つぎへ」ボタンを おして ください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const nextBtn = document.querySelector('button[type="submit"], button:contains("つぎへ")');
                    if (nextBtn) {
                        tutorialHelper.monitorButtonClick(nextBtn, null, () => {
                            tutorialOverlay.close();
                            sessionStorage.removeItem(tutorialManager.FLAGS.SEIKAI_SAVE);
                        });
                    }
                }
            }
        ];
    }

    // ふせいかい名前入力
    function getFuseikaiCreateSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'システムの なまえを にゅうりょくします。<br><br>「ふせいかい」と にゅうりょくして、<br>「つぎへ」ボタンを おして ください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const nextBtn = document.querySelector('button[type="submit"], button:contains("つぎへ")');
                    if (nextBtn) {
                        tutorialHelper.monitorButtonClick(nextBtn, null, () => {
                            tutorialOverlay.close();
                            sessionStorage.removeItem(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        // せいかい名前入力
        tutorialManager.register('seikai_create', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.SEIKAI_SAVE
            },
            steps: getSeikaiiCreateSteps,
            onComplete: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.SEIKAI_SAVE);
            },
            onSkip: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.SEIKAI_SAVE);
                return true;
            }
        });

        // ふせいかい名前入力
        tutorialManager.register('fuseikai_create', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.FUSEIKAI_SAVE
            },
            steps: getFuseikaiCreateSteps,
            onComplete: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.FUSEIKAI_SAVE);
            },
            onSkip: function () {
                sessionStorage.removeItem(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                return true;
            }
        });

        console.log('📝 名前入力チュートリアル登録完了');
    }

})();
