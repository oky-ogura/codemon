/**
 * tutorial_save.js - 保存完了画面用チュートリアル
 * save.htmlで使用
 */

(function () {
    'use strict';

    // せいかい保存完了
    function getSeikaiiSaveSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: '「せいかい」システムが ほぞん されました！🎉<br><br>それでは、システムいちらんに もどりましょう。',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const listBtn = document.querySelector('a[href*="system/list"], a[onclick*="location.href"]');
                    if (listBtn) {
                        tutorialHelper.monitorButtonClick(listBtn, null, () => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                        });
                    } else {
                        // 自動的にリダイレクトされる場合
                        setTimeout(() => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                        }, 2000);
                    }
                }
            }
        ];
    }

    // ふせいかい保存完了
    function getFuseikaiSaveSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: '「ふせいかい」システムが ほぞん されました！🎉<br><br>それでは、システムいちらんに もどりましょう。',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const listBtn = document.querySelector('a[href*="system/list"], a[onclick*="location.href"]');
                    if (listBtn) {
                        tutorialHelper.monitorButtonClick(listBtn, null, () => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                        });
                    } else {
                        setTimeout(() => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                        }, 2000);
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        // せいかい保存完了
        tutorialManager.register('seikai_save', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.SEIKAI_SAVE,
                forbidFlag: tutorialManager.FLAGS.SEIKAI_SAVED
            },
            steps: getSeikaiiSaveSteps,
            onComplete: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                tutorialManager.removeFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
            },
            onSkip: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                tutorialManager.removeFlag(tutorialManager.FLAGS.SEIKAI_SAVE);
                return true;
            }
        });

        // ふせいかい保存完了
        tutorialManager.register('fuseikai_save', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.FUSEIKAI_SAVE,
                forbidFlag: tutorialManager.FLAGS.FUSEIKAI_SAVED
            },
            steps: getFuseikaiSaveSteps,
            onComplete: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                tutorialManager.removeFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
            },
            onSkip: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                tutorialManager.removeFlag(tutorialManager.FLAGS.FUSEIKAI_SAVE);
                return true;
            }
        });

        console.log('📝 保存完了チュートリアル登録完了');
    }

})();
