/**
 * tutorial_block.js - アルゴリズム保存画面用チュートリアル
 * block_create.htmlで使用
 */

(function () {
    'use strict';

    // アルゴリズム保存手順
    function getBlockSaveSteps() {
        return [
            {
                target: '#blockName',
                message: 'アルゴリズムの なまえを きめましょう。<br>「じょうけんはんてい」と<br>にゅうりょく してください！',
                onShow: function () {
                    // 名前入力欄にフォーカス
                    const nameInput = document.querySelector('#blockName');
                    if (nameInput) nameInput.focus();
                }
            },
            {
                target: '#blockDetail',
                message: 'どんな アルゴリズムか<br>せつめいを かきましょう。<br>たとえば「せいかい・ふせいかいを はんてい」<br>などと かいてみましょう！',
                onShow: function () {
                    // 詳細入力欄にフォーカス
                    const detailInput = document.querySelector('#blockDetail');
                    if (detailInput) detailInput.focus();
                }
            },
            {
                target: '#saveBtn',
                message: 'なまえと せつめいが かけたら、<br>「ほぞんする」ボタンを<br>おして ほぞん してください！',
                showNextButton: false, // ボタンクリック待ち
                onShow: function () {
                    const saveBtn = document.querySelector('#saveBtn');
                    if (saveBtn) {
                        // クリックを監視して完了処理
                        tutorialHelper.monitorButtonClick(saveBtn, null, () => {
                            tutorialOverlay.close();
                            // 保存ボタンが押されたら完了フラグを立てる（あるいは次のステップへ）
                            // ここが最終ステップなら COMPLETED フラグを設定
                            if (window.tutorialManager) {
                                // 既存のフラグをクリア
                                sessionStorage.removeItem(tutorialManager.FLAGS.ALGORITHM_SAVED);
                                // 完了フラグをセット
                                tutorialManager.setFlag(tutorialManager.FLAGS.COMPLETED);
                            }
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('block_save', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.ALGORITHM_SAVED
            },
            steps: getBlockSaveSteps,
            onComplete: function () {
                // 完了時の処理（ボタンクリック監視で処理済みだが、予備）
                sessionStorage.removeItem(tutorialManager.FLAGS.ALGORITHM_SAVED);
                tutorialManager.setFlag(tutorialManager.FLAGS.COMPLETED);
            },
            onSkip: function () {
                // スキップ時の処理
                sessionStorage.removeItem(tutorialManager.FLAGS.ALGORITHM_SAVED);
                tutorialManager.setFlag(tutorialManager.FLAGS.COMPLETED);
                return true;
            }
        });

        console.log('📝 アルゴリズム保存チュートリアル登録完了');
    }

})();
