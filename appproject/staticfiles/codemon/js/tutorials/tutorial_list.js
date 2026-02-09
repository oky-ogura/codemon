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
                target: '#btn-new',
                message: 'それでは、つぎに「ふせいかい」システムを つくりましょう！<br><br>この<strong>「＋ あたらしく つくる」ボタン</strong>を おして ください！',
                messagePosition: 'bottom',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    // アニメーション完了を待つ
                    setTimeout(() => {
                        const createBtn = document.getElementById('btn-new');
                        if (createBtn) {
                            // ハイライト位置を更新
                            tutorialOverlay.positionHighlight(createBtn);
                            tutorialOverlay.positionOverlayParts(createBtn);

                            tutorialHelper.monitorButtonClick(createBtn, null, () => {
                                tutorialOverlay.close();
                                // 古いSTARTフラグを削除してからFUSEIKAI_CREATEフラグを設定
                                tutorialManager.removeFlag(tutorialManager.FLAGS.START);
                                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_CREATE);
                            });
                        }
                    }, 300);
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
                target: '#btn-new',
                message: 'それでは、さいごに「もんだい」システムを つくりましょう！<br><br>この<strong>「＋ あたらしく つくる」ボタン</strong>を おして ください！',
                messagePosition: 'bottom',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    // アニメーション完了を待つ
                    setTimeout(() => {
                        const createBtn = document.getElementById('btn-new');
                        if (createBtn) {
                            // ハイライト位置を更新
                            tutorialOverlay.positionHighlight(createBtn);
                            tutorialOverlay.positionOverlayParts(createBtn);

                            tutorialHelper.monitorButtonClick(createBtn, null, () => {
                                tutorialOverlay.close();
                                // 古いフラグを削除してからMONDAI_CREATEフラグを設定
                                tutorialManager.removeFlag(tutorialManager.FLAGS.START);
                                tutorialManager.removeFlag(tutorialManager.FLAGS.FUSEIKAI_CREATE);
                                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
                            });
                        }
                    }, 300);
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
