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
                target: '#formBtn',
                message: 'まず、フォームボタンを クリックして、<br>メニューを ひらいてください！',
                requireClick: true,
                showNextButton: false,
                showSkip: true
            },
            {
                target: '#addCheckboxBtn',
                message: 'つぎに、チェックボックスを ついかします！<br><br>「チェックボックス」ボタンを クリックして ください。',
                messagePosition: 'bottom',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    setTimeout(() => {
                        const checkboxBtn = document.getElementById('addCheckboxBtn');
                        console.log('🎯 addCheckboxBtn要素:', checkboxBtn);
                        if (checkboxBtn) {
                            const rect = checkboxBtn.getBoundingClientRect();
                            console.log(`📏 addCheckboxBtn位置: top=${rect.top}, left=${rect.left}, width=${rect.width}, height=${rect.height}`);
                            console.log('🔄 位置更新を実行');
                            tutorialOverlay.positionHighlight(checkboxBtn);
                            tutorialOverlay.positionOverlayParts(checkboxBtn);

                            // クリックを監視（直接イベントリスナー追加）
                            const clickHandler = function () {
                                console.log('🎯 チェックボックスボタンがクリックされました - パネル待機開始');
                                checkboxBtn.removeEventListener('click', clickHandler);

                                // オプションパネルが開くのを待つ
                                const waitForPanel = setInterval(() => {
                                    const optionsPanel = document.getElementById('createOptionsPanel');
                                    const optionsCount = document.getElementById('optionsCount');
                                    console.log('🔍 パネル要素検索中:', optionsPanel, optionsCount);
                                    if (optionsPanel && optionsPanel.classList.contains('show') && optionsCount) {
                                        clearInterval(waitForPanel);
                                        console.log('✅ オプションパネルが開きました - 次のステップへ');
                                        setTimeout(() => {
                                            tutorialOverlay.next();
                                        }, 300); // パネルアニメーション完了を待つ
                                    }
                                }, 100);
                            };

                            tutorialHelper.addSafeEventListener(checkboxBtn, 'click', clickHandler);
                        } else {
                            console.warn('⚠️ addCheckboxBtn要素が見つかりません');
                        }
                    }, 300);
                }
            },
            {
                target: '#optionsLabel',
                message: 'オプションパネルが ひらきましたね！<br><br>「ラベル」に 「1+1は?」と にゅうりょくして ください。',
                messagePosition: 'top',
                nextText: null,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 ラベル入力待機');

                    setTimeout(() => {
                        const labelInput = document.getElementById('optionsLabel');
                        if (labelInput) {
                            const rect = labelInput.getBoundingClientRect();
                            console.log(`📏 optionsLabel位置: top=${rect.top}, left=${rect.left}, width=${rect.width}, height=${rect.height}`);
                            tutorialOverlay.positionHighlight(labelInput);
                            tutorialOverlay.positionOverlayParts(labelInput);

                            // 現在の値を確認
                            console.log('📝 現在の入力値:', labelInput.value.trim());
                            // 全角を半角に変換
                            const normalizedValue = labelInput.value.trim()
                                .replace(/[０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0))
                                .replace(/[Ａ-Ｚａ-ｚ]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0))
                                .replace(/？/g, '?')
                                .replace(/＋/g, '+');
                            console.log('🔄 正規化後:', normalizedValue);
                            if (normalizedValue === '1+1は?') {
                                console.log('✅ すでにラベルが入力されています');
                                setTimeout(() => tutorialOverlay.next(), 500);
                                return;
                            }
                        }
                    }, 300);

                    const checkLabelInput = setInterval(() => {
                        const labelInput = document.getElementById('optionsLabel');
                        if (labelInput) {
                            const currentValue = labelInput.value.trim();
                            console.log('🔍 入力値チェック:', currentValue);

                            // 全角を半角に変換
                            const normalizedValue = currentValue
                                .replace(/[０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0))
                                .replace(/[Ａ-Ｚａ-ｚ]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0))
                                .replace(/？/g, '?')
                                .replace(/＋/g, '+');
                            if (normalizedValue === '1+1は?') {
                                clearInterval(checkLabelInput);
                                console.log('✅ ラベル入力完了: 1+1は? (正規化前:', currentValue, ')');
                                setTimeout(() => tutorialOverlay.next(), 500);
                            }
                        }
                    }, 100);

                    // チュートリアルがクローズされたときにインターバルをクリア
                    window.tutorialState = window.tutorialState || {};
                    window.tutorialState.labelInputInterval = checkLabelInput;
                }
            },
            {
                target: '#createOptionsConfirm',
                message: 'それでは「作成」ボタンを おして、チェックボックスを つくりましょう！',
                messagePosition: 'left',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    setTimeout(() => {
                        const confirmBtn = document.getElementById('createOptionsConfirm');
                        console.log('🎯 createOptionsConfirm要素:', confirmBtn);
                        if (confirmBtn) {
                            const rect = confirmBtn.getBoundingClientRect();
                            console.log(`📏 createOptionsConfirm位置: top=${rect.top}, left=${rect.left}, width=${rect.width}, height=${rect.height}`);
                            tutorialOverlay.positionHighlight(confirmBtn);
                            tutorialOverlay.positionOverlayParts(confirmBtn);

                            // クリックを監視
                            const clickHandler = function () {
                                console.log('🎯 作成ボタンがクリックされました');
                                confirmBtn.removeEventListener('click', clickHandler);

                                // チェックボックスが配置されるまで少し待ってから次へ
                                setTimeout(() => {
                                    console.log('✅ 次のステップへ進みます');
                                    tutorialOverlay.next();
                                }, 800); // チェックボックス配置のアニメーション待ち
                            };

                            tutorialHelper.addSafeEventListener(confirmBtn, 'click', clickHandler);
                        } else {
                            console.warn('⚠️ createOptionsConfirm要素が見つかりません');
                        }
                    }, 300);
                }
            },
            {
                target: '.checkbox-group',
                message: 'チェックボックスが がめんに でてきましたね！<br><br>「1+1は?」の こたえとして、こうもくを へんしゅうしましょう。',
                messagePosition: 'top',
                nextText: 'つぎへ',
                showSkip: true,
                onShow: function () {
                    console.log('🎯 チェックボックス配置確認');

                    // チェックボックスが配置されるまで少し待って位置を更新
                    setTimeout(() => {
                        const checkbox = document.querySelector('.checkbox-group');
                        console.log('🎯 checkbox-group要素:', checkbox);
                        if (checkbox) {
                            const rect = checkbox.getBoundingClientRect();
                            console.log(`📏 checkbox-group位置: top=${rect.top}, left=${rect.left}, width=${rect.width}, height=${rect.height}`);
                            console.log('✅ チェックボックスが配置されました');
                            tutorialOverlay.positionHighlight(checkbox);
                            tutorialOverlay.positionOverlayParts(checkbox);
                        } else {
                            console.warn('⚠️ チェックボックスが見つかりません');
                        }
                    }, 500);
                }
            },
            {
                target: '.checkbox-group',
                message: 'チェックボックスの こうもくを へんしゅうします。<br><br>「こうもく」という もじを けして、すうじだけに しましょう！<br><br>たとえば「こうもく1」→「1」のように へんしゅうして ください。<br>3つとも おなじように へんしゅうしたら「つぎへ」を おして ください。',
                messagePosition: 'top',
                nextText: 'つぎへ',
                showSkip: true,
                onShow: function () {
                    setTimeout(() => {
                        const checkbox = document.querySelector('.checkbox-group');
                        console.log('🎯 checkbox-group要素(項目編集):', checkbox);
                        if (checkbox) {
                            const rect = checkbox.getBoundingClientRect();
                            console.log(`📏 checkbox-group位置: top=${rect.top}, left=${rect.left}, width=${rect.width}, height=${rect.height}`);
                            tutorialOverlay.positionHighlight(checkbox);
                            tutorialOverlay.positionOverlayParts(checkbox);
                        }
                    }, 300);
                }
            },
            {
                target: '#addButtonBtn',
                message: 'つぎは、「ボタン」を ついかします！<br><br>「ボタン」を クリックして ください。',
                requireClick: true,
                showSkip: true
            },
            {
                target: null,
                centerMessage: false,
                message: 'モーダルが ひらきましたね！<br><br>したに スクロールして「作成」ボタンを おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 作成ボタンクリック待機');

                    // オーバーレイは表示せず、左パネルだけ表示
                    // showFullOverlay()を呼ばないことで、モーダルが隠れない

                    // メッセージを表示（ハイライトなしで左パネルに表示）
                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // モーダルのz-indexをチュートリアルパネルより上に設定
                    const setModalZIndex = () => {
                        // 様々なモーダル要素を検索
                        const modalOverlay = document.querySelector('.modal-overlay');
                        const modalDialog = document.querySelector('.custom-confirm-dialog');
                        const allOverlays = document.querySelectorAll('[class*="overlay"]');
                        const allModals = document.querySelectorAll('[class*="modal"], [class*="dialog"], [class*="confirm"]');

                        console.log('🔍 モーダル関連要素検索結果:');
                        console.log('  .modal-overlay:', modalOverlay ? 'found' : 'NOT FOUND');
                        console.log('  .custom-confirm-dialog:', modalDialog ? 'found' : 'NOT FOUND');
                        console.log('  [class*="overlay"]の数:', allOverlays.length);
                        console.log('  [class*="modal/dialog/confirm"]の数:', allModals.length);

                        // すべてのオーバーレイ要素のz-indexを上げる
                        allOverlays.forEach((el, index) => {
                            const currentZIndex = window.getComputedStyle(el).zIndex;
                            if (currentZIndex !== 'auto' && parseInt(currentZIndex) >= 100000) {
                                el.style.setProperty('z-index', '150001', 'important');
                                console.log(`  📏 オーバーレイ${index}: ${el.className} → z-index: 150001 (元: ${currentZIndex})`);
                            }
                        });

                        // すべてのモーダル/ダイアログ要素のz-indexを上げる
                        allModals.forEach((el, index) => {
                            const currentZIndex = window.getComputedStyle(el).zIndex;
                            if (currentZIndex !== 'auto' && parseInt(currentZIndex) >= 100000) {
                                el.style.setProperty('z-index', '150004', 'important');
                                console.log(`  📏 モーダル${index}: ${el.className} → z-index: 150004 (元: ${currentZIndex})`);
                            }
                        });

                        // 特定の要素も確実に設定
                        if (modalDialog) {
                            modalDialog.style.setProperty('z-index', '150004', 'important');
                            const computedZIndex = window.getComputedStyle(modalDialog).zIndex;
                            console.log('📏 .custom-confirm-dialog のz-index設定完了:', computedZIndex);
                        }
                    };

                    // 即座に設定
                    setModalZIndex();

                    // 100ms後にも再設定
                    setTimeout(setModalZIndex, 100);

                    // 200ms後にも再設定
                    setTimeout(setModalZIndex, 200);

                    setTimeout(() => {
                        const createBtn = document.querySelector('.custom-confirm-dialog button.confirm');
                        console.log('🎯 作成ボタン要素:', createBtn);
                        if (createBtn) {
                            // クリックを監視（ハイライトなし）
                            const clickHandler = function () {
                                console.log('🎯 作成ボタンがクリックされました');
                                createBtn.removeEventListener('click', clickHandler);

                                // モーダル関連要素のz-indexを元に戻す
                                const allOverlays = document.querySelectorAll('[class*="overlay"]');
                                const allModals = document.querySelectorAll('[class*="modal"], [class*="dialog"], [class*="confirm"]');

                                allOverlays.forEach(el => el.style.removeProperty('z-index'));
                                allModals.forEach(el => el.style.removeProperty('z-index'));

                                console.log('🔄 すべてのモーダル関連要素のz-indexをリセット');

                                // ボタンが配置されるまで少し待ってから次へ
                                setTimeout(() => {
                                    console.log('✅ 次のステップへ進みます');
                                    tutorialOverlay.next();
                                }, 800);
                            };

                            tutorialHelper.addSafeEventListener(createBtn, 'click', clickHandler);
                        }
                    }, 300);
                }
            },
            // STEP10: ボタンを右クリック
            {
                target: null,
                centerMessage: false,
                message: 'さきほど つくった ボタンを<br>右クリック してください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 ボタン右クリック待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        // waitForElementを使って確実にボタンを検出
                        const customButton = await tutorialOverlay.waitForElement(
                            '#slideArea button.draggable-btn',
                            {
                                timeout: 10000,
                                visible: true
                            }
                        );

                        console.log('✅ ボタンを発見:', customButton);
                        console.log('  クラス:', customButton.className);
                        console.log('  テキスト:', customButton.textContent);

                        // メッセージとハイライトを先に表示（スクロールなし）
                        tutorialOverlay.showMessage(step, customButton);
                        tutorialOverlay.highlight(customButton);
                        console.log('✅ メッセージとハイライトを表示しました');

                        // 右クリックを監視
                        const rightClickHandler = function (e) {
                            console.log('✅ ボタンが右クリックされました');
                            customButton.removeEventListener('contextmenu', rightClickHandler);
                            tutorialOverlay.removeHighlight();

                            // コンテキストメニューが表示されるのを待ってから次へ
                            setTimeout(() => {
                                console.log('✅ 次のステップへ進みます');
                                tutorialOverlay.next();
                            }, 500);
                        };

                        customButton.addEventListener('contextmenu', rightClickHandler);
                        console.log('✅ 右クリックイベントリスナーを登録しました');
                    } else {
                        console.error('❌ draggable-btnボタンが見つかりません');

                        // デバッグ情報を出力
                        const allButtons = slideArea.querySelectorAll('button');
                        console.log('🔍 slideArea内のボタン数:', allButtons.length);
                        allButtons.forEach((btn, i) => {
                            console.log(`  button[${i}]:`, {
                                tag: btn.tagName,
                                class: btn.className,
                                id: btn.id,
                                text: btn.textContent.trim()
                            });
                        });

                        const userConfirm = confirm('作成したボタンが見つかりませんでした。\nこのステップをスキップしますか？');
                        if(userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
            }
            },
    // STEP11: アルゴリズム新規作成メニュー選択
    {
        target: null,
            centerMessage: false,
                message: 'コンテキストメニューが ひらきましたね！<br><br>「アルゴリズムを しんきさくせい」を クリック してください！',
                    requireClick: false,
                        showNextButton: false,
                            showSkip: true,
                                onShow: function () {
                                    console.log('🎯 アルゴリズム新規作成メニュー待機');

                                    // メッセージを表示
                                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                                    tutorialOverlay.showMessage(step, null);

                                    // コンテキストメニュー項目のクリックを監視
                                    const checkMenu = () => {
                                        // コンテキストメニュー内の「アルゴリズムを新規作成」を探す
                                        const menuItems = document.querySelectorAll('.context-menu-item, [role="menuitem"]');

                                        menuItems.forEach(item => {
                                            const text = item.textContent.trim();
                                            if (text.includes('アルゴリズム') && text.includes('新規作成')) {
                                                console.log('🎯 アルゴリズム新規作成メニュー項目を発見:', item);

                                                const clickHandler = function () {
                                                    console.log('✅ アルゴリズム新規作成がクリックされました');
                                                    item.removeEventListener('click', clickHandler);

                                                    // アルゴリズム作成画面への遷移を待つ
                                                    // 次のチュートリアルに引き継ぐためのフラグを設定
                                                    sessionStorage.setItem('tutorial_mondai_to_algorithm', 'true');
                                                    console.log('🚩 アルゴリズムチュートリアル開始フラグを設定');

                                                    // チュートリアル終了
                                                    setTimeout(() => {
                                                        tutorialOverlay.close();
                                                        tutorialManager.setFlag(tutorialManager.FLAGS.MONDAI_CREATE);
                                                    }, 500);
                                                };

                                                item.addEventListener('click', clickHandler);
                                            }
                                        });
                                    };

                                    // メニューが表示されるまで待機
                                    const menuInterval = setInterval(() => {
                                        const contextMenu = document.querySelector('.context-menu, [role="menu"]');
                                        if (contextMenu) {
                                            clearInterval(menuInterval);
                                            checkMenu();
                                        }
                                    }, 100);

                                    // 10秒経ってもメニューが見つからなければタイムアウト
                                    setTimeout(() => {
                                        clearInterval(menuInterval);
                                    }, 10000);
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

}) ();
