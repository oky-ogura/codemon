/**
 * tutorial_mondai.js - もんだいチュートリアル
 * 
 * STEP2チュートリアルの3番目のフェーズ
 * もんだい画面の作成方法を教える（チェックボックス＋ボタン）
 */

(function () {
    'use strict';

    function getMondaiSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'さいごに「もんだい」がめんを つくりましょう！<br><br>クイズの もんだいを だして、こたえを えらんで もらいます。',
                nextText: 'つぎへ'
            },
            {
                target: '#checkboxBtn',
                message: 'まず、チェックボックスを ついかします！<br><br>「チェックボックス」ボタンを クリックして ください。',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'モーダルが ひらきましたね！<br><br>「ラベル」に 「1+1は?」と にゅうりょくして ください。',
                nextText: null,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 ラベル入力待機');

                    const checkLabelInput = setInterval(() => {
                        const labelInput = document.querySelector('input[name="groupLabel"]');
                        if (labelInput && labelInput.value === '1+1は?') {
                            clearInterval(checkLabelInput);
                            console.log('✅ ラベル入力完了: 1+1は?');
                            setTimeout(() => tutorialOverlay.next(), 500);
                        }
                    }, 100);
                }
            },
            {
                target: null,
                centerMessage: true,
                message: '「こうもくすう」が 「3」に なって いることを かくにんして ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: '.custom-confirm-dialog button:first-of-type',
                message: 'それでは「OK」ボタンを おして、チェックボックスを つくりましょう！',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'チェックボックスが がめんに でてきましたね！<br><br>つぎは、このチェックボックスの なかみを へんしゅうします。',
                nextText: null,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 チェックボックス配置確認');

                    try {
                        const checkbox = await tutorialHelper.waitForElement('.checkbox-group', 5000);
                        console.log('✅ チェックボックスが配置されました:', checkbox);
                        window.tutorialState.createdCheckbox = checkbox;
                        setTimeout(() => tutorialOverlay.next(), 1000);
                    } catch (error) {
                        console.warn('⚠️ チェックボックスが見つかりませんでした');
                        tutorialOverlay.next();
                    }
                }
            },
            {
                target: null,
                centerMessage: true,
                message: 'チェックボックスの こうもくを へんしゅうします。<br><br>「こうもく」という もじを けして、すうじだけに しましょう！<br><br>たとえば「こうもく1」→「1」のように へんしゅうして ください。<br>3つとも おなじように へんしゅうしたら「つぎへ」を おして ください。',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: '#addButtonBtn',
                message: 'つぎは、「ボタン」を ついかします！<br><br>「ボタン」を クリックして ください。',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'ボタンの ラベルを にゅうりょくする モーダルが ひらきましたね！<br><br>「こたえを チェック」と にゅうりょくして ください。',
                nextText: null,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 ボタンラベル入力待機');

                    const checkButtonLabel = setInterval(() => {
                        const labelInput = document.querySelector('input[type="text"]');
                        if (labelInput && labelInput.value === 'こたえを チェック') {
                            clearInterval(checkButtonLabel);
                            console.log('✅ ボタンラベル入力完了');
                            setTimeout(() => tutorialOverlay.next(), 500);
                        }
                    }, 100);
                }
            },
            {
                target: '.custom-confirm-dialog button:first-of-type',
                message: '「OK」ボタンを おして、ボタンを がめんに ついかしましょう！',
                requireClick: true,
                showSkip: true
            },
            {
                target: '#saveBtn',
                message: 'すばらしい！<br><br>それでは、ほぞんボタンを おして、<br>「もんだい」という なまえで ほぞん してください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    console.log('💾 保存ボタン説明（もんだい）');

                    const saveBtn = document.getElementById('saveBtn');
                    if (saveBtn) {
                        tutorialOverlay.positionHighlight(saveBtn);
                        tutorialOverlay.positionOverlayParts(saveBtn);

                        tutorialHelper.monitorButtonClick(saveBtn, null, () => {
                            console.log('✅ 保存ボタンがクリックされました（もんだい）');
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('mondai', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.MONDAI_CREATE,
                forbidFlag: tutorialManager.FLAGS.MONDAI_CREATED
            },
            steps: getMondaiSteps,
            onComplete: function () {
                console.log('🎉 もんだいチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATED);
            },
            onSkip: function () {
                if (confirm('チュートリアルを とちゅうで やめますか？')) {
                    tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATED);
                    return true;
                }
                return false;
            }
        });

        console.log('📝 もんだいチュートリアル登録完了');
    }

})();
