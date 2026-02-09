/**
 * アルゴリズム実行テストチュートリアル
 * 
 * システム編集画面でアルゴリズムの動作確認を行います
 * - 作成したボタンの実行ボタンをクリック
 * - チェックボックスで「2」を選択 → 「せいかい」システム表示確認
 * - チェックボックスで「3」を選択 → 「ふせいかい」システム表示確認
 * - 閉じるボタンで戻る
 * - 保存ボタンで問題に保存
 */

(function () {
    'use strict';

    function getAlgorithmExecutionSteps() {
        return [
            // STEP1: ウェルカムメッセージ
            {
                target: null,
                centerMessage: true,
                message: 'アルゴリズムが できました！<br><br>つぎは、うごくか テストして みましょう！',
                nextText: 'つぎへ',
                showSkip: false,
                onShow: function () {
                    console.log('🎯 アルゴリズム実行テストチュートリアル開始');
                }
            },
            // STEP2: 実行ボタンをクリック
            {
                target: null,
                centerMessage: false,
                message: 'さっき つくった ボタンの<br>「じっこう」ボタンを おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 実行ボタンクリック待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        // カスタムボタン配下の実行ボタンを探す
                        const executeButton = await tutorialOverlay.waitForElement('.btn-execute, button:contains("実行")', {
                            timeout: 10000,
                            visible: true
                        });

                        if (executeButton) {
                            tutorialOverlay.showMessage(step, executeButton);
                            tutorialOverlay.highlight(executeButton);

                            executeButton.addEventListener('click', function onExecuteClick() {
                                console.log('✅ 実行ボタンがクリックされました');
                                executeButton.removeEventListener('click', onExecuteClick);
                                tutorialOverlay.removeHighlight();

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }, { once: true });
                        }
                    } catch (error) {
                        console.error('❌ 実行ボタンが見つかりません:', error);
                        const userConfirm = confirm('実行ボタンが見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP3: チェックボックス「2」を選択
            {
                target: null,
                centerMessage: false,
                message: 'チェックボックスで「2」を<br>えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 チェックボックス「2」選択待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // チェックボックスの変更を監視
                    const checkCheckbox = setInterval(() => {
                        // 「2」に対応するチェックボックスを探す
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        for (const checkbox of checkboxes) {
                            // チェックボックスのラベルや値をチェック
                            const label = checkbox.parentElement?.textContent || '';
                            if (label.includes('2') && checkbox.checked) {
                                console.log('✅ チェックボックス「2」が選択されました');
                                clearInterval(checkCheckbox);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 800);
                                return;
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkCheckbox), 30000);
                }
            },
            // STEP4: 「せいかい」システムが表示されたことを確認
            {
                target: null,
                centerMessage: true,
                message: '「せいかい」が ひょうじされましたね！<br><br>アルゴリズムが ただしく うごいて います！',
                nextText: 'つぎへ',
                showSkip: false,
                onShow: function () {
                    console.log('🎯 せいかいシステム表示確認');

                    // 3秒後に自動で次へ
                    setTimeout(() => {
                        tutorialOverlay.next();
                    }, 3000);
                }
            },
            // STEP5: チェックボックス「3」を選択
            {
                target: null,
                centerMessage: false,
                message: 'つぎは、チェックボックスで「3」を<br>えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 チェックボックス「3」選択待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // チェックボックスの変更を監視
                    const checkCheckbox = setInterval(() => {
                        // 「3」に対応するチェックボックスを探す
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        for (const checkbox of checkboxes) {
                            // チェックボックスのラベルや値をチェック
                            const label = checkbox.parentElement?.textContent || '';
                            if (label.includes('3') && checkbox.checked) {
                                console.log('✅ チェックボックス「3」が選択されました');
                                clearInterval(checkCheckbox);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 800);
                                return;
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkCheckbox), 30000);
                }
            },
            // STEP6: 「ふせいかい」システムが表示されたことを確認
            {
                target: null,
                centerMessage: true,
                message: 'こんどは「ふせいかい」が ひょうじされましたね！<br><br>アルゴリズムが かんぺきです！',
                nextText: 'つぎへ',
                showSkip: false,
                onShow: function () {
                    console.log('🎯 ふせいかいシステム表示確認');

                    // 3秒後に自動で次へ
                    setTimeout(() => {
                        tutorialOverlay.next();
                    }, 3000);
                }
            },
            // STEP7: 閉じるボタンをクリック
            {
                target: null,
                centerMessage: false,
                message: 'それでは、「とじる」ボタンを<br>おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 閉じるボタンクリック待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const closeButton = await tutorialOverlay.waitForElement('.btn-close, button:contains("閉じる"), .modal-footer .btn-secondary', {
                            timeout: 10000,
                            visible: true
                        });

                        if (closeButton) {
                            tutorialOverlay.showMessage(step, closeButton);
                            tutorialOverlay.highlight(closeButton);

                            closeButton.addEventListener('click', function onCloseClick() {
                                console.log('✅ 閉じるボタンがクリックされました');
                                closeButton.removeEventListener('click', onCloseClick);
                                tutorialOverlay.removeHighlight();

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }, { once: true });
                        }
                    } catch (error) {
                        console.error('❌ 閉じるボタンが見つかりません:', error);
                        const userConfirm = confirm('閉じるボタンが見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP8: システム編集画面に戻ったことを確認
            {
                target: null,
                centerMessage: true,
                message: 'テストが かんりょうしました！<br><br>では、もんだいに ほぞんしましょう！',
                nextText: 'つぎへ',
                showSkip: false,
                onShow: function () {
                    console.log('🎯 システム編集画面に戻りました');

                    // 2秒後に自動で次へ
                    setTimeout(() => {
                        tutorialOverlay.next();
                    }, 2000);
                }
            },
            // STEP9: 保存ボタンをクリック
            {
                target: null,
                centerMessage: false,
                message: '「ほぞん」ボタンを おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 保存ボタンクリック待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const saveButton = await tutorialOverlay.waitForElement('button:contains("保存"), .btn-save, #save-button', {
                            timeout: 10000,
                            visible: true
                        });

                        if (saveButton) {
                            tutorialOverlay.showMessage(step, saveButton);
                            tutorialOverlay.highlight(saveButton);

                            saveButton.addEventListener('click', function onSaveClick() {
                                console.log('✅ 保存ボタンがクリックされました');
                                saveButton.removeEventListener('click', onSaveClick);
                                tutorialOverlay.removeHighlight();

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }, { once: true });
                        }
                    } catch (error) {
                        console.error('❌ 保存ボタンが見つかりません:', error);
                        const userConfirm = confirm('保存ボタンが見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP10: 保存先「もんだい」入力
            {
                target: null,
                centerMessage: false,
                message: 'ほぞんさきに<br>「もんだい」と にゅうりょくして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 保存先入力待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const nameInput = await tutorialOverlay.waitForElement('#id_name, input[name="name"]', {
                            timeout: 10000,
                            visible: true
                        });

                        if (nameInput) {
                            tutorialOverlay.showMessage(step, nameInput);
                            tutorialOverlay.highlight(nameInput);

                            // 入力を監視
                            const checkInput = setInterval(() => {
                                const currentValue = nameInput.value.trim();
                                console.log('🔍 現在の入力値:', currentValue);

                                if (currentValue === 'もんだい') {
                                    console.log('✅ 正しい名前が入力されました');
                                    clearInterval(checkInput);
                                    tutorialOverlay.removeHighlight();

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }, 500);

                            // 30秒でタイムアウト
                            setTimeout(() => clearInterval(checkInput), 30000);
                        }
                    } catch (error) {
                        console.error('❌ 名前入力欄が見つかりません:', error);
                        const userConfirm = confirm('名前入力欄が見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP11: 説明「チュートリアルもんだい」入力
            {
                target: null,
                centerMessage: false,
                message: 'せつめいに<br>「チュートリアルもんだい」と にゅうりょくして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 説明入力待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const descInput = await tutorialOverlay.waitForElement('#id_description, textarea[name="description"]', {
                            timeout: 10000,
                            visible: true
                        });

                        if (descInput) {
                            tutorialOverlay.showMessage(step, descInput);
                            tutorialOverlay.highlight(descInput);

                            // 入力を監視
                            const checkInput = setInterval(() => {
                                const currentValue = descInput.value.trim();
                                console.log('🔍 現在の説明:', currentValue);

                                if (currentValue === 'チュートリアルもんだい') {
                                    console.log('✅ 正しい説明が入力されました');
                                    clearInterval(checkInput);
                                    tutorialOverlay.removeHighlight();

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }, 500);

                            // 30秒でタイムアウト
                            setTimeout(() => clearInterval(checkInput), 30000);
                        }
                    } catch (error) {
                        console.error('❌ 説明入力欄が見つかりません:', error);
                        const userConfirm = confirm('説明入力欄が見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP12: 保存ダイアログの保存ボタンクリック
            {
                target: null,
                centerMessage: false,
                message: 'ほぞん ボタンを おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 ダイアログ保存ボタンクリック待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const saveDialogButton = await tutorialOverlay.waitForElement('.modal-footer button.btn-primary, button[type="submit"]', {
                            timeout: 10000,
                            visible: true
                        });

                        if (saveDialogButton) {
                            tutorialOverlay.showMessage(step, saveDialogButton);
                            tutorialOverlay.highlight(saveDialogButton);

                            saveDialogButton.addEventListener('click', function onDialogSaveClick() {
                                console.log('✅ ダイアログ保存ボタンがクリックされました');
                                saveDialogButton.removeEventListener('click', onDialogSaveClick);
                                tutorialOverlay.removeHighlight();

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }, { once: true });
                        }
                    } catch (error) {
                        console.error('❌ ダイアログ保存ボタンが見つかりません:', error);
                        const userConfirm = confirm('ダイアログ保存ボタンが見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP13: 完了メッセージ
            {
                target: null,
                centerMessage: true,
                message: 'おめでとうございます！<br><br>チュートリアルが すべて かんりょうしました！<br><br>これで、あなたも アルゴリズムマスターです！',
                nextText: 'かんりょう',
                showSkip: false,
                onShow: function () {
                    console.log('✅ アルゴリズム実行テストチュートリアル完了');
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('algorithm_execution', {
            trigger: {
                customCheck: function () {
                    // algorithm_advancedチュートリアルから引き継いだフラグをチェック
                    const flag = sessionStorage.getItem('tutorial_algorithm_to_execution');
                    if (flag === 'true') {
                        console.log('✅ アルゴリズム実行テストチュートリアル開始条件を満たしました');
                        sessionStorage.removeItem('tutorial_algorithm_to_execution');
                        return true;
                    }
                    return false;
                }
            },
            steps: getAlgorithmExecutionSteps,
            tutorialName: 'algorithm_execution', // 進捗追跡を有効化
            onComplete: function () {
                console.log('🎉 アルゴリズム実行テストチュートリアル完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_SAVED);
            },
            onSkip: function () {
                console.log('⏭️ アルゴリズム実行テストチュートリアルをスキップ');
                tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_SAVED);
                return true;
            }
        });

        console.log('📝 アルゴリズム実行テストチュートリアル登録完了');
    }

})();
