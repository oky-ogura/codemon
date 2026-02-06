/**
 * tutorial_test.js - テスト実行チュートリアル
 * system_list.htmlで使用
 */

(function () {
    'use strict';

    function getTestSteps() {
        return [
            {
                target: null,
                centerMessage: true,
                message: 'おめでとう ございます！🎉<br><br>アルゴリズムが ほぞん されました！<br><br>つぎは、つくった「もんだい」システムを<br>じっさいに テストして みましょう！',
                nextText: 'つぎへ',
                showSkip: false
            },
            {
                target: null,
                centerMessage: true,
                message: 'システムいちらんから<br>「もんだい」システムを さがして ください！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: '「もんだい」システムの カードに マウスを のせると、<br>「じっこう」ボタンが でてきます！<br><br>「じっこう」ボタンを おして、<br>システムを テストして みましょう！',
                nextText: null,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 実行ボタン待機');

                    const checkPreview = setInterval(() => {
                        const previewModal = document.querySelector('.preview-overlay');
                        if (previewModal && previewModal.style.display !== 'none') {
                            clearInterval(checkPreview);
                            console.log('✅ プレビュー画面が開きました');
                            setTimeout(() => tutorialOverlay.next(), 1000);
                        }
                    }, 100);
                }
            },
            {
                target: null,
                centerMessage: true,
                message: 'プレビュー画面が ひらきましたね！<br><br>「2」を えらんで、<br>「こたえを チェック」ボタンを おして みましょう！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: '「せいかい！」が ひょうじ されましたね！🎉<br><br>つぎは「1」や「3」を えらんで テストして みてください。',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: '「ふせいかい！」が ひょうじ されましたね！<br><br>クイズシステムが ただしく うごいて いますね！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: null,
                centerMessage: true,
                message: 'STEP2チュートリアル かんりょう！おめでとう ございます！🎉<br><br>これで クイズシステムの つくりかたが わかりましたね！',
                nextText: 'おわる',
                showSkip: false
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('test', {
            trigger: {
                requireFlag: tutorialManager.FLAGS.ALGORITHM_SAVED,
                forbidFlag: tutorialManager.FLAGS.COMPLETED
            },
            steps: getTestSteps,
            onComplete: function () {
                console.log('🎉 STEP2チュートリアル完了！');
                tutorialManager.setFlag(tutorialManager.FLAGS.COMPLETED);

                sessionStorage.removeItem(tutorialManager.FLAGS.ALGORITHM_SAVED);

                alert('STEP2チュートリアル かんりょう！おめでとう ございます！🎉');
            },
            onSkip: function () {
                tutorialManager.setFlag(tutorialManager.FLAGS.COMPLETED);
                sessionStorage.removeItem(tutorialManager.FLAGS.ALGORITHM_SAVED);
                return true;
            }
        });

        console.log('📝 テスト実行チュートリアル登録完了');
    }

})();
