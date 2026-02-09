/**
 * tutorial_list.js - 一覧画面用チュートリアル
 * system_list.htmlで使用（せいかい＆ふせいかい一覧）
 */

(function () {
    'use strict';

    // せいかい一覧チュートリアル
    function getSeikaiiListSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: '「せいかい」システムが ほぞん されました！<br><br>システムいちらんに ひょうじ されて いますね。',
                nextText: 'つぎへ',
                showSkip: false
            },
            {
                target: null,
                centerMessage: true,
                message: 'それでは、つぎに「ふせいかい」システムを つくりましょう！<br><br>「＋ あたらしく つくる」ボタンを おして ください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const createBtn = document.querySelector('a[href*="system/create"]');
                    if (createBtn) {
                        tutorialHelper.monitorButtonClick(createBtn, null, () => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_CREATE);
                        });
                    }
                }
            }
        ];
    }

    // ふせいかい一覧チュートリアル
    function getFuseikaiListSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: '「ふせいかい」システムも ほぞん されました！<br><br>いちらんに 2つの システムが ひょうじ されて いますね。',
                nextText: 'つぎへ',
                showSkip: false
            },
            {
                target: null,
                centerMessage: true,
                message: 'それでは、さいごに「もんだい」システムを つくりましょう！<br><br>「＋ あたらしく つくる」ボタンを おして ください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const createBtn = document.querySelector('a[href*="system/create"]');
                    if (createBtn) {
                        tutorialHelper.monitorButtonClick(createBtn, null, () => {
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        // せいかい一覧チュートリアル
        tutorialManager.register('seikai_list', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.SEIKAI_SAVED,
                forbidFlag: tutorialManager.FLAGS.FUSEIKAI_CREATE
            },
            steps: getSeikaiiListSteps,
            onComplete: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_CREATE);
            },
            onSkip: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_CREATE);
                return true;
            }
        });

        // ふせいかい一覧チュートリアル
        tutorialManager.register('fuseikai_list', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.FUSEIKAI_SAVED,
                forbidFlag: tutorialManager.FLAGS.MONDAI_LIST
            },
            steps: getFuseikaiListSteps,
            onComplete: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_LIST);
                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
            },
            onSkip: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_LIST);
                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
                return true;
            }
        });

        console.log('📝 一覧チュートリアル登録完了');
    }

})();
