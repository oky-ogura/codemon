/**
 * せいかいチュートリアル（SimpleTutorial版）
 */

(function () {
    'use strict';

    // システム編集画面でのみ起動
    if (!window.location.href.includes('/system/')) {
        console.log('⏭️ せいかいチュートリアル: システム編集画面ではありません');
        return;
    }

    // 既に完了している場合はスキップ
    if (localStorage.getItem('simple_tutorial_seikai_completed') === 'true') {
        console.log('✅ せいかいチュートリアル: 既に完了しています');
        return;
    }

    // ページ読み込み完了を待つ
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTutorial);
    } else {
        initTutorial();
    }

    function initTutorial() {
        console.log('🎬 せいかいチュートリアル準備開始');

        const steps = [
            // STEP1: 開始メッセージ
            {
                message: 'それでは、じっさいに クイズシステムを つくって みましょう！<br><br>まずは 「せいかい」が でたときの がめんを つくります。',
                nextText: 'はじめる',
                showSkip: true
            },

            // STEP2: 実行ボタンの説明
            {
                target: '#executeBtn',
                message: 'これは じっこうボタンだよ。<br>つくった システムを うごかすことが できるよ。',
                nextText: 'わかった',
                showSkip: true
            },

            // STEP3: 保存ボタンの説明
            {
                target: '#saveBtn',
                message: 'これは ほぞんボタンだよ。<br>つくった システムを ほぞんするときに つかうよ。',
                nextText: 'わかった',
                showSkip: true
            },

            // STEP4: 図形ボタンをクリック
            {
                target: '#shapeBtn',
                message: 'それでは、せいかいがめんを つくりましょう！<br><br>まずは まるい かたちを えらびます。<br><br>この ずけい ボタンを クリックして、<br>メニューを ひらいてください！',
                requireClick: true,
                showSkip: true
            },

            // STEP5: 円ボタンをクリック
            {
                target: '#addCircleBtn',
                message: 'メニューから「えん」を クリックして ください！',
                requireClick: true,
                showSkip: true
            },

            // STEP6: 円を右クリックして編集
            {
                message: 'まるが がめんに でてきましたね！<br><br>つぎは、この まるを みぎクリックして、<br>「へんしゅう」パネルを ひらいてください。',
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    try {
                        // 円が配置されるのを待つ
                        const circle = await this.waitForElement('[data-shape-type="circle"]', 5000);
                        console.log('✅ 円を検出しました:', circle);

                        // 円をハイライト
                        const rect = circle.getBoundingClientRect();
                        this.highlightBox.style.cssText = `
                            position: fixed;
                            left: ${rect.left - 5}px;
                            top: ${rect.top - 5}px;
                            width: ${rect.width + 10}px;
                            height: ${rect.height + 10}px;
                            border: 3px solid #4CAF50;
                            border-radius: 50%;
                            box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
                            z-index: 150001;
                            pointer-events: none;
                            display: block;
                        `;

                        // 右クリックを待つ
                        circle.addEventListener('contextmenu', async (e) => {
                            console.log('✅ 円が右クリックされました');

                            // 編集パネルの出現を待つ
                            try {
                                await this.waitForElement('.shape-settings-panel', 3000);
                                console.log('✅ 編集パネルが表示されました');
                                setTimeout(() => this.next(), 500);
                            } catch (err) {
                                console.warn('⚠️ 編集パネルが見つかりませんでしたが続行します');
                                setTimeout(() => this.next(), 500);
                            }
                        }, { once: true });

                    } catch (error) {
                        console.error('❌ 円の検出に失敗:', error);
                        alert('円が見つかりませんでした。\n手動で円を配置してから右クリックしてください。');
                    }
                }
            },

            // STEP7: 色とサイズを変更
            {
                target: '.shape-settings-panel',
                message: 'すばらしい！<br><br>それでは、まるの「いろ」と「おおきさ」を かえましょう！<br><br><strong>【いろ】</strong><br>RGBで <strong>255, 0, 0</strong> と にゅうりょくするか、<br>カラーピッカーで <strong>あか</strong>を えらんでください。<br><br><strong>【おおきさ】</strong><br><strong>150</strong> に してください。<br><br>できたら、したの <strong>「てきよう」ボタン</strong>を おしてください！',
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    // 適用ボタンのクリックを待つ
                    const checkApply = setInterval(() => {
                        const applyBtn = document.querySelector('.shape-settings-panel button');
                        if (applyBtn && applyBtn.textContent.includes('適用')) {
                            applyBtn.addEventListener('click', () => {
                                console.log('✅ 適用ボタンがクリックされました');
                                clearInterval(checkApply);
                                setTimeout(() => this.next(), 500);
                            }, { once: true });
                            clearInterval(checkApply);
                        }
                    }, 500);

                    setTimeout(() => clearInterval(checkApply), 30000);
                }
            },

            // STEP8: テキストボタンをクリック
            {
                target: '#textBtn',
                message: 'つぎは、もじを ついかします！<br><br>「テキスト」ボタンを クリックして ください！',
                requireClick: true,
                showSkip: true
            },

            // STEP9: テキストを入力
            {
                message: 'テキストボックスが でてきましたね！<br><br>「せいかい！」と にゅうりょくして、<br>Enterキーを おしてください！',
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    try {
                        const textInput = await this.waitForElement('input[type="text"]', 5000);
                        console.log('✅ テキスト入力欄を検出');

                        textInput.addEventListener('keypress', (e) => {
                            if (e.key === 'Enter' && textInput.value.includes('せいかい')) {
                                console.log('✅ 正しいテキストが入力されました');
                                setTimeout(() => this.next(), 500);
                            }
                        });

                    } catch (error) {
                        console.warn('⚠️ テキスト入力欄が見つかりません');
                        setTimeout(() => this.next(), 3000);
                    }
                }
            },

            // STEP10: 完了
            {
                message: 'よく できました！<br><br>これで「せいかい」がめんが かんせいしました！<br><br>「ほぞん」ボタンを おして、<br>「せいかい」という なまえで ほぞんして ください！',
                nextText: 'チュートリアル完了',
                showSkip: false
            }
        ];

        // チュートリアル開始（1秒後）
        setTimeout(() => {
            const tutorial = new SimpleTutorial(steps, {
                onComplete: () => {
                    console.log('🎉 せいかいチュートリアル完了');
                    localStorage.setItem('simple_tutorial_seikai_completed', 'true');
                }
            });
            tutorial.start();
        }, 1000);
    }

})();
