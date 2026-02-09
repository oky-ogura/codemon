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
                target: '#btn-list',
                message: '「せいかい」システムが ほぞん されました！🎉<br><br>それでは、この<strong>「つくったものリストへ」ボタン</strong>を おして ください！',
                messagePosition: 'top',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    // アニメーション完了を待つ
                    setTimeout(() => {
                        const listBtn = document.getElementById('btn-list');
                        console.log('🎯 btn-list要素:', listBtn);
                        if (listBtn) {
                            console.log('📏 btn-list位置:', listBtn.getBoundingClientRect());
                            // ハイライト位置を更新
                            tutorialOverlay.positionHighlight(listBtn);
                            // オーバーレイパーツも更新
                            tutorialOverlay.positionOverlayParts(listBtn);

                            tutorialHelper.monitorButtonClick(listBtn, null, () => {
                                tutorialOverlay.close();
                                tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                            });
                        } else {
                            console.warn('⚠️ btn-list要素が見つかりません');
                            // 自動的にリダイレクトされる場合
                            setTimeout(() => {
                                tutorialOverlay.close();
                                tutorialManager.setFlag(tutorialManager.FLAGS.SEIKAI_SAVED);
                            }, 2000);
                        }
                    }, 600); // アニメーション完了後(0.5s + 余裕)
                }
            }
        ];
    }

    // ふせいかい保存完了
    function getFuseikaiSaveSteps() {
        return [
            {
                target: '#btn-list',
                message: '「ふせいかい」システムが ほぞん されました！🎉<br><br>それでは、この<strong>「つくったものリストへ」ボタン</strong>を おして ください！',
                messagePosition: 'top',
                nextText: null,
                showNextButton: false,
                requireClick: false,
                onShow: function () {
                    // アニメーション完了を待つ
                    setTimeout(() => {
                        const listBtn = document.getElementById('btn-list');
                        console.log('🎯 btn-list要素:', listBtn);
                        if (listBtn) {
                            console.log('📏 btn-list位置:', listBtn.getBoundingClientRect());
                            // ハイライト位置を更新
                            tutorialOverlay.positionHighlight(listBtn);
                            // オーバーレイパーツも更新
                            tutorialOverlay.positionOverlayParts(listBtn);

                            tutorialHelper.monitorButtonClick(listBtn, null, () => {
                                tutorialOverlay.close();
                                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                            });
                        } else {
                            console.warn('⚠️ btn-list要素が見つかりません');
                            setTimeout(() => {
                                tutorialOverlay.close();
                                tutorialManager.setFlag(tutorialManager.FLAGS.FUSEIKAI_SAVED);
                            }, 2000);
                        }
                    }, 600); // アニメーション完了後(0.5s + 余裕)
                }
            }
        ];
    }

    if (window.tutorialManager) {
        // せいかい保存完了
        tutorialManager.register('seikai_save', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.SEIKAI_SAVE,
                forbidFlag: tutorialManager.FLAGS.SEIKAI_SAVED,
                // 作成画面（名前入力）などでは実行しない
                condition: function () {
                    return !document.querySelector('.create-panel');
                }
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
                forbidFlag: tutorialManager.FLAGS.FUSEIKAI_SAVED,
                // 作成画面（名前入力）などでは実行しない
                condition: function () {
                    return !document.querySelector('.create-panel');
                }
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
