/**
 * tutorial_algorithm.js - アルゴリズムチュートリアル
 * block/index.htmlで使用
 */

(function () {
    'use strict';

    function getAlgorithmSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'それでは、アルゴリズムを つくりましょう！<br><br>ブロックを つかって、クイズの ロジックを つくります。',
                nextText: 'つぎへ'
            },
            {
                target: '.blocklyTreeRow',
                message: 'ひだりの メニューから「システム」を えらんで ください！',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: '「システムじょうけん」ブロックを<br>みぎの さぎょうエリアに ドラッグして ください！',
                nextText: null,
                showSkip: true,
                onShow: async function () {
                    try {
                        await tutorialHelper.waitForElement('[data-id*="system_condition"]', 10000);
                        window.tutorialState.systemConditionBlock = true;
                        setTimeout(() => tutorialOverlay.next(), 500);
                    } catch (error) {
                        console.warn('⚠️ system_conditionブロックが見つかりませんでした');
                        tutorialOverlay.next();
                    }
                }
            },
            {
                target: null,
                centerMessage: true,
                message: 'つぎに、「ラベル」の ところで<br>「1+1は?」を えらんで ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'じょうけんを せっていします！<br><br>「が」の あとの ぷるだうんから<br>「2」を えらんで ください。',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'つぎは、せいかいのときに ひょうじする システムを えらびます！<br><br>「システムをひょうじ」ブロックを<br>「すること」の なかに ドラッグして ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: '「システムをひょうじ」ブロックで<br>「せいかい」を えらんで ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'おなじように、「そうでなければ」の なかにも<br>「システムをひょうじ」ブロックを ついかして、<br>「ふせいかい」を えらんで ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'すばらしい！<br><br>アルゴリズムが できました！<br><br>それでは、ほぞんボタンを おして ください！',
                nextText: null,
                showNextButton: false,
                onShow: function () {
                    const saveBtn = document.querySelector('[onclick*="saveBlock"]');
                    if (saveBtn) {
                        tutorialHelper.monitorButtonClick(saveBtn, null, () => {
                            console.log('✅ アルゴリズム保存ボタンがクリックされました');
                            tutorialOverlay.close();
                            tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_SAVED);
                        });
                    }
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('algorithm', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.MONDAI_CREATED,
                forbidFlag: tutorialManager.FLAGS.ALGORITHM_SAVED
            },
            steps: getAlgorithmSteps,
            onComplete: function () {
                console.log('🎉 アルゴリズムチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_SAVED);
            },
            onSkip: function () {
                if (confirm('チュートリアルをスキップしますか？')) {
                    tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_SAVED);
                    return true;
                }
                return false;
            }
        });

        console.log('📝 アルゴリズムチュートリアル登録完了');
    }

    window.tutorialState = window.tutorialState || {};

})();
