/**
 * アルゴリズム作成チュートリアル（応用編）
 * mondaiチュートリアルから継続して実行される
 */

(function () {
    'use strict';

    function getAlgorithmAdvancedSteps() {
        return [
            // STEP1: システムカテゴリを開く
            {
                target: null,
                centerMessage: true,
                message: 'アルゴリズムさくせい がめんに いどうしましたね！<br><br>ここで、もんだいの ロジックを つくります！',
                nextText: 'つぎへ',
                showSkip: true
            },
            {
                target: '.blocklyTreeRow',
                message: 'ひだりの メニューから<br>「システム」を クリック してください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 システムカテゴリクリック待機');

                    // システムカテゴリを探す
                    tutorialOverlay.waitForElement('.blocklyTreeRow', {
                        timeout: 10000,
                        validator: (el) => el.textContent.includes('システム')
                    }).then(systemCategory => {
                        console.log('✅ システムカテゴリを発見:', systemCategory);

                        const clickHandler = function () {
                            console.log('✅ システムカテゴリがクリックされました');
                            systemCategory.removeEventListener('click', clickHandler);

                            setTimeout(() => {
                                tutorialOverlay.next();
                            }, 500);
                        };

                        systemCategory.addEventListener('click', clickHandler);
                    }).catch(error => {
                        console.error('❌ システムカテゴリが見つかりません:', error);
                    });
                }
            },
            // STEP3: system_conditionブロックをドラッグ
            {
                target: null,
                centerMessage: true,
                message: '「もし システム〇〇の～」ブロックを<br>みぎの ワークスペースに<br>ドラッグ してください！',
                nextText: null,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 system_conditionブロック配置待機');

                    // ワークスペースにブロックが配置されるのを監視
                    const checkInterval = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');

                            if (systemConditionBlock) {
                                console.log('✅ system_conditionブロックが配置されました');
                                clearInterval(checkInterval);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 800);
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkInterval), 30000);
                }
            },
            // STEP4: システム選択（仮保存）
            {
                target: null,
                centerMessage: false,
                message: 'ブロックの さいしょの リストで<br>「仮保存」を えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 システム選択（仮保存）待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // システム選択の変更を監視
                    const checkSystemSelection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');

                            if (systemConditionBlock) {
                                const systemIdValue = systemConditionBlock.getFieldValue('SYSTEM_ID');
                                console.log('🔍 現在のシステムID:', systemIdValue);

                                // 仮保存（0以外のID）が選択されたか確認
                                if (systemIdValue && systemIdValue !== '0') {
                                    console.log('✅ システムが選択されました:', systemIdValue);
                                    clearInterval(checkSystemSelection);

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkSystemSelection), 30000);
                }
            },
            // STEP5: ラベル選択（1+1は?）
            {
                target: null,
                centerMessage: false,
                message: 'つぎの リストで<br>「1+1は?」を えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 ラベル選択（1+1は?）待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // ラベル選択の変更を監視
                    const checkLabelSelection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');

                            if (systemConditionBlock) {
                                const elementNameValue = systemConditionBlock.getFieldValue('ELEMENT_NAME');
                                console.log('🔍 現在のラベル:', elementNameValue);

                                // ラベルが選択されたか確認（JSONパース試行）
                                if (elementNameValue && elementNameValue !== '') {
                                    try {
                                        const labelData = JSON.parse(elementNameValue);
                                        if (labelData.label && labelData.label.includes('1+1')) {
                                            console.log('✅ ラベル「1+1は?」が選択されました');
                                            clearInterval(checkLabelSelection);

                                            setTimeout(() => {
                                                tutorialOverlay.next();
                                            }, 800);
                                        }
                                    } catch (e) {
                                        // JSON以外の形式の場合
                                        if (elementNameValue.includes('1+1')) {
                                            console.log('✅ ラベル「1+1は?」が選択されました');
                                            clearInterval(checkLabelSelection);

                                            setTimeout(() => {
                                                tutorialOverlay.next();
                                            }, 800);
                                        }
                                    }
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkLabelSelection), 30000);
                }
            },
            // STEP6: 項目選択（2）
            {
                target: null,
                centerMessage: false,
                message: 'その した「項目：」リストで<br>「2」を えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 項目選択（2）待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // 項目選択の変更を監視
                    const checkItemSelection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');

                            if (systemConditionBlock) {
                                const item0Value = systemConditionBlock.getFieldValue('ITEM_0');
                                console.log('🔍 現在の項目:', item0Value);

                                // 「2」が選択されたか確認
                                if (item0Value && item0Value === '2') {
                                    console.log('✅ 項目「2」が選択されました');
                                    clearInterval(checkItemSelection);

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkItemSelection), 30000);
                }
            },
            // STEP7: display_systemブロック（せいかい）の説明
            {
                target: null,
                centerMessage: false,
                message: 'つぎは、システムを ひょうじ ブロックを<br>つかいます。<br><br>システムタブから「システムを ひょうじ」<br>ブロックを おしてください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 display_system説明');
                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    setTimeout(() => {
                        tutorialOverlay.next();
                    }, 3000);
                }
            },
            // STEP8: システムタブクリック（2回目）
            {
                target: null,
                centerMessage: false,
                message: '「システム」タブを クリックして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 システムタブクリック待機（2回目）');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    try {
                        const systemTab = await tutorialOverlay.waitForElement('.blocklyTreeRow', {
                            timeout: 10000,
                            visible: true,
                            validator: (el) => el.textContent && el.textContent.includes('システム')
                        });

                        if (systemTab) {
                            tutorialOverlay.showMessage(step, systemTab);
                            tutorialOverlay.highlight(systemTab);

                            systemTab.addEventListener('click', function onSystemTabClick() {
                                console.log('✅ システムタブがクリックされました（2回目）');
                                systemTab.removeEventListener('click', onSystemTabClick);
                                tutorialOverlay.removeHighlight();

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 500);
                            }, { once: true });
                        }
                    } catch (error) {
                        console.error('❌ システムタブが見つかりません:', error);
                        const userConfirm = confirm('システムタブが見つかりませんでした。\nこのステップをスキップしますか？');
                        if (userConfirm) {
                            tutorialOverlay.next();
                        }
                    }
                }
            },
            // STEP9: display_systemブロックをワークスペースにドラッグ
            {
                target: null,
                centerMessage: false,
                message: '「システムを ひょうじ」ブロックを<br>ワークスペースに ドラッグして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 display_systemブロックのドラッグ待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    let displaySystemBlockFound = false;

                    // ブロック追加を監視
                    const checkDisplaySystem = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const displaySystemBlock = blocks.find(b => b.type === 'display_system');

                            if (displaySystemBlock && !displaySystemBlockFound) {
                                console.log('✅ display_systemブロックが追加されました');
                                displaySystemBlockFound = true;
                                clearInterval(checkDisplaySystem);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 800);
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkDisplaySystem), 30000);
                }
            },
            // STEP10: display_systemブロックのシステムリスト選択（せいかい）
            {
                target: null,
                centerMessage: false,
                message: 'システムリストで<br>「せいかい」を えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 display_systemブロック：せいかい選択待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // システム選択の変更を監視
                    const checkSeikaiSelection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const displaySystemBlock = blocks.find(b => b.type === 'display_system');

                            if (displaySystemBlock) {
                                const systemIdValue = displaySystemBlock.getFieldValue('SYSTEM_ID');
                                console.log('🔍 現在のシステムID:', systemIdValue);

                                // 「せいかい」のシステムIDをチェック（仮にID=1とする）
                                // TODO: 実際のシステムIDを確認する必要がある
                                if (systemIdValue && systemIdValue !== '0') {
                                    console.log('✅ システム（せいかい）が選択されました');
                                    clearInterval(checkSeikaiSelection);

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkSeikaiSelection), 30000);
                }
            },
            // STEP11: display_systemブロックをsystem_conditionのDO部分にドラッグ
            {
                target: null,
                centerMessage: false,
                message: 'この「システムを ひょうじ」ブロックを<br>「もし システム〇〇の～」ブロックの<br>うえがわ（すること）に ドラッグして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 display_systemブロックの接続待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // ブロック接続を監視
                    const checkConnection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');
                            const displaySystemBlock = blocks.find(b => b.type === 'display_system');

                            if (systemConditionBlock && displaySystemBlock) {
                                // DO部分に接続されているかチェック
                                const doInput = systemConditionBlock.getInput('DO');
                                if (doInput && doInput.connection && doInput.connection.isConnected()) {
                                    console.log('✅ display_systemブロックが接続されました');
                                    clearInterval(checkConnection);

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkConnection), 30000);
                }
            },
            // STEP12: display_systemブロックを複製（右クリック→複製）
            {
                target: null,
                centerMessage: false,
                message: 'いま おいた「システムを ひょうじ」ブロックを<br>みぎクリックして、「ふくせい」を<br>えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 display_systemブロック複製待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    let initialBlockCount = 0;
                    const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                    if (workspace) {
                        const displayBlocks = workspace.getAllBlocks().filter(b => b.type === 'display_system');
                        initialBlockCount = displayBlocks.length;
                        console.log('🔍 現在のdisplay_systemブロック数:', initialBlockCount);
                    }

                    // ブロック数の増加を監視
                    const checkDuplicate = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const displayBlocks = workspace.getAllBlocks().filter(b => b.type === 'display_system');
                            const currentCount = displayBlocks.length;

                            if (currentCount > initialBlockCount) {
                                console.log('✅ display_systemブロックが複製されました');
                                clearInterval(checkDuplicate);

                                setTimeout(() => {
                                    tutorialOverlay.next();
                                }, 800);
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkDuplicate), 30000);
                }
            },
            // STEP13: 複製したブロックのシステムリスト変更（ふせいかい）
            {
                target: null,
                centerMessage: false,
                message: 'ふくせいした ブロックの システムリストで<br>「ふせいかい」を えらんで ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 複製ブロック：ふせいかい選択待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    let seikaiBlockId = null;
                    let fusekaiFound = false;

                    // 既存のせいかいブロックのIDを記録
                    const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                    if (workspace) {
                        const blocks = workspace.getAllBlocks();
                        const systemConditionBlock = blocks.find(b => b.type === 'system_condition');
                        if (systemConditionBlock) {
                            const doInput = systemConditionBlock.getInput('DO');
                            if (doInput && doInput.connection && doInput.connection.targetBlock()) {
                                seikaiBlockId = doInput.connection.targetBlock().id;
                                console.log('🔍 せいかいブロックID:', seikaiBlockId);
                            }
                        }
                    }

                    // 新しいブロックのシステム選択を監視
                    const checkFusekaiSelection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const displayBlocks = blocks.filter(b => b.type === 'display_system');

                            // せいかいブロック以外のdisplay_systemブロックをチェック
                            for (const block of displayBlocks) {
                                if (block.id !== seikaiBlockId) {
                                    const systemIdValue = block.getFieldValue('SYSTEM_ID');
                                    console.log('🔍 複製ブロックのシステムID:', systemIdValue);

                                    // システムIDが変更されたかチェック（せいかいと異なるID）
                                    if (systemIdValue && systemIdValue !== '0' && !fusekaiFound) {
                                        console.log('✅ システム（ふせいかい）が選択されました');
                                        fusekaiFound = true;
                                        clearInterval(checkFusekaiSelection);

                                        setTimeout(() => {
                                            tutorialOverlay.next();
                                        }, 800);
                                    }
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkFusekaiSelection), 30000);
                }
            },
            // STEP14: 複製したブロックをELSE部分にドラッグ
            {
                target: null,
                centerMessage: false,
                message: 'この「ふせいかい」ブロックを<br>「もし システム〇〇の～」ブロックの<br>したがわ（でなければ）に ドラッグして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 ELSE部分への接続待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // ELSE接続を監視
                    const checkElseConnection = setInterval(() => {
                        const workspace = window.Blockly ? Blockly.getMainWorkspace() : null;
                        if (workspace) {
                            const blocks = workspace.getAllBlocks();
                            const systemConditionBlock = blocks.find(b => b.type === 'system_condition');

                            if (systemConditionBlock) {
                                // ELSE部分に接続されているかチェック
                                const elseInput = systemConditionBlock.getInput('ELSE');
                                if (elseInput && elseInput.connection && elseInput.connection.isConnected()) {
                                    console.log('✅ ELSE部分にブロックが接続されました');
                                    clearInterval(checkElseConnection);

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkElseConnection), 30000);
                }
            },
            // STEP15: 保存ボタンを押す
            {
                target: null,
                centerMessage: false,
                message: 'よく できました！<br><br>では、「ほぞん」ボタンを おして ください！',
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
            // STEP16: アルゴリズム名入力
            {
                target: null,
                centerMessage: false,
                message: 'アルゴリズムめいに<br>「チュートリアル」と にゅうりょくして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 アルゴリズム名入力待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];

                    // モーダルが表示されるまで待機
                    try {
                        const nameInput = await tutorialOverlay.waitForElement('#id_name, input[name="name"]', {
                            timeout: 10000,
                            visible: true
                        });

                        if (nameInput) {
                            tutorialOverlay.showMessage(step, nameInput);
                            tutorialOverlay.highlight(nameInput);

                            // 入力を監視
                            const checkNameInput = setInterval(() => {
                                const currentValue = nameInput.value.trim();
                                console.log('🔍 現在の入力値:', currentValue);

                                if (currentValue === 'チュートリアル') {
                                    console.log('✅ 正しい名前が入力されました');
                                    clearInterval(checkNameInput);
                                    tutorialOverlay.removeHighlight();

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }, 500);

                            // 30秒でタイムアウト
                            setTimeout(() => clearInterval(checkNameInput), 30000);
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
            // STEP17: アルゴリズム説明入力
            {
                target: null,
                centerMessage: false,
                message: 'せつめいに<br>「チュートリアルぶんき」と にゅうりょくして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: async function () {
                    console.log('🎯 アルゴリズム説明入力待機');

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
                            const checkDescInput = setInterval(() => {
                                const currentValue = descInput.value.trim();
                                console.log('🔍 現在の説明:', currentValue);

                                if (currentValue === 'チュートリアルぶんき') {
                                    console.log('✅ 正しい説明が入力されました');
                                    clearInterval(checkDescInput);
                                    tutorialOverlay.removeHighlight();

                                    setTimeout(() => {
                                        tutorialOverlay.next();
                                    }, 800);
                                }
                            }, 500);

                            // 30秒でタイムアウト
                            setTimeout(() => clearInterval(checkDescInput), 30000);
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
            // STEP18: 保存ダイアログの保存ボタンクリック
            {
                target: null,
                centerMessage: false,
                message: 'それでは、ほぞん ボタンを おして ください！',
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

                                // sessionStorageに次のチュートリアルフラグを設定
                                sessionStorage.setItem('tutorial_algorithm_to_execution', 'true');

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
            // STEP19: Chromeダイアログの「はい」ボタン待機
            {
                target: null,
                centerMessage: true,
                message: '「アルゴリズムの ほぞんが かんりょうしました。<br>システムへんしゅうがめんに もどりますか？」と<br>でたら、「はい」を おして ください！',
                requireClick: false,
                showNextButton: false,
                showSkip: true,
                onShow: function () {
                    console.log('🎯 Chromeダイアログ「はい」待機');

                    const step = tutorialOverlay.steps[tutorialOverlay.currentStep];
                    tutorialOverlay.showMessage(step, null);

                    // ページ遷移を検知（システム編集画面に戻る）
                    const checkPageTransition = setInterval(() => {
                        // URLに "system" が含まれているかチェック
                        if (window.location.href.includes('/system/')) {
                            console.log('✅ システム編集画面に戻りました');
                            clearInterval(checkPageTransition);

                            setTimeout(() => {
                                tutorialOverlay.next();
                            }, 800);
                        }
                    }, 500);

                    // 30秒でタイムアウト
                    setTimeout(() => clearInterval(checkPageTransition), 30000);
                }
            },
            // ここまで実装完了 - 続きは次のステップで
            {
                target: null,
                centerMessage: true,
                message: 'よく できました！<br><br>つづきは じゅんびちゅうです...',
                nextText: 'おわる',
                showSkip: false,
                onShow: function () {
                    console.log('✅ アルゴリズムチュートリアル（Part1）完了');
                }
            }
        ];
    }

    if (window.tutorialManager) {
        tutorialManager.register('algorithm_advanced', {
            trigger: {
                customCheck: function () {
                    // mondaiチュートリアルから引き継いだフラグをチェック
                    const flag = sessionStorage.getItem('tutorial_mondai_to_algorithm');
                    if (flag === 'true') {
                        console.log('✅ アルゴリズムチュートリアル開始条件を満たしました');
                        sessionStorage.removeItem('tutorial_mondai_to_algorithm');
                        return true;
                    }
                    return false;
                }
            },
            steps: getAlgorithmAdvancedSteps,
            tutorialName: 'algorithm_advanced', // 進捗追跡を有効化
            onComplete: function () {
                console.log('🎉 アルゴリズムチュートリアル（応用編）完了');
                tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_ADVANCED_COMPLETED);
            },
            onSkip: function () {
                console.log('⏭️ アルゴリズムチュートリアル（応用編）をスキップ');
                tutorialManager.setFlag(tutorialManager.FLAGS.ALGORITHM_ADVANCED_COMPLETED);
                return true;
            }
        });

        console.log('📝 アルゴリズムチュートリアル（応用編）登録完了');
    }

})();
