/**
 * TutorialManager - チュートリアル統括マネージャー
 * 
 * STEP2チュートリアル全体を管理し、フラグチェーンと状態を統一管理します
 */

class TutorialManager {
    constructor() {
        // フラグ定義（チェーン順）
        this.FLAGS = {
            // 開始フラグ
            START: 'tutorial_step2_start',

            // せいかいフェーズ
            SEIKAI_SAVE: 'tutorial_step2_seikai_save',
            SEIKAI_SAVED: 'tutorial_step2_seikai_saved',

            // ふせいかいフェーズ
            FUSEIKAI_CREATE: 'tutorial_step2_fuseikai_create',
            FUSEIKAI_SAVE: 'tutorial_step2_fuseikai_save',
            FUSEIKAI_SAVED: 'tutorial_step2_fuseikai_saved',

            // もんだいフェーズ
            MONDAI_LIST: 'tutorial_step2_mondai_list',
            MONDAI_CREATE: 'tutorial_step2_mondai_create',
            MONDAI_CREATED: 'tutorial_step2_mondai_created',

            // アルゴリズムフェーズ
            ALGORITHM_SAVED: 'tutorial_step2_algorithm_saved',

            // 完了フラグ
            COMPLETED: 'tutorial_step2_completed'
        };

        // フラグチェーン（順序を明確に）
        this.FLAG_CHAIN = [
            this.FLAGS.START,
            this.FLAGS.SEIKAI_SAVE,
            this.FLAGS.SEIKAI_SAVED,
            this.FLAGS.FUSEIKAI_CREATE,
            this.FLAGS.FUSEIKAI_SAVE,
            this.FLAGS.FUSEIKAI_SAVED,
            this.FLAGS.MONDAI_LIST,
            this.FLAGS.MONDAI_CREATE,
            this.FLAGS.MONDAI_CREATED,
            this.FLAGS.ALGORITHM_SAVED,
            this.FLAGS.COMPLETED
        ];

        // 登録済みチュートリアル
        this.tutorials = new Map();

        // 現在実行中のチュートリアル
        this.activeTutorial = null;
    }

    // ========================================
    // フラグ管理
    // ========================================

    /**
     * フラグをチェック
     */
    hasFlag(flagName) {
        return sessionStorage.getItem(flagName) === 'true';
    }

    /**
     * フラグを設定
     */
    setFlag(flagName, value = 'true') {
        sessionStorage.setItem(flagName, value);
        console.log(`✅ フラグ設定: ${flagName} = ${value}`);
    }

    /**
     * フラグを削除
     */
    removeFlag(flagName) {
        sessionStorage.removeItem(flagName);
        console.log(`🗑️ フラグ削除: ${flagName}`);
    }

    /**
     * 全チュートリアルフラグを削除
     */
    clearAllFlags() {
        this.FLAG_CHAIN.forEach(flag => this.removeFlag(flag));
        console.log('🗑️ 全チュートリアルフラグをクリアしました');
    }

    /**
     * 現在のフラグ状態を取得
     */
    getFlagStatus() {
        const status = {};
        this.FLAG_CHAIN.forEach(flag => {
            status[flag] = this.hasFlag(flag);
        });
        return status;
    }

    /**
     * フラグチェーンの進行状況を取得（0-100%）
     */
    getProgress() {
        const setFlags = this.FLAG_CHAIN.filter(flag => this.hasFlag(flag)).length;
        return Math.round((setFlags / this.FLAG_CHAIN.length) * 100);
    }

    /**
     * 次に設定すべきフラグを取得
     */
    getNextFlag() {
        for (const flag of this.FLAG_CHAIN) {
            if (!this.hasFlag(flag)) {
                return flag;
            }
        }
        return null; // 全て完了
    }

    /**
     * 現在のフェーズを取得
     */
    getCurrentPhase() {
        if (this.hasFlag(this.FLAGS.COMPLETED)) return 'completed';
        if (this.hasFlag(this.FLAGS.ALGORITHM_SAVED)) return 'test';
        if (this.hasFlag(this.FLAGS.MONDAI_CREATED)) return 'algorithm';
        if (this.hasFlag(this.FLAGS.MONDAI_CREATE)) return 'mondai_input';
        if (this.hasFlag(this.FLAGS.MONDAI_LIST)) return 'mondai_list';
        if (this.hasFlag(this.FLAGS.FUSEIKAI_SAVED)) return 'mondai_create';
        if (this.hasFlag(this.FLAGS.FUSEIKAI_SAVE)) return 'fuseikai_save';
        if (this.hasFlag(this.FLAGS.FUSEIKAI_CREATE)) return 'fuseikai';
        if (this.hasFlag(this.FLAGS.SEIKAI_SAVED)) return 'seikai_list';
        if (this.hasFlag(this.FLAGS.SEIKAI_SAVE)) return 'seikai_save';
        if (this.hasFlag(this.FLAGS.START)) return 'seikai';
        return 'not_started';
    }

    // ========================================
    // チュートリアル登録・実行
    // ========================================

    /**
     * チュートリアルを登録
     * 
     * @param {string} name - チュートリアル名
     * @param {Object} config - チュートリアル設定
     */
    register(name, config) {
        if (!config.trigger || !config.steps) {
            console.error('❌ チュートリアル設定が不正です:', name);
            return;
        }

        this.tutorials.set(name, config);
        console.log(`📝 チュートリアル登録: ${name}`);
    }

    /**
     * チュートリアルを自動開始（フラグに基づく）
     * 
     * ページ読み込み時に呼び出される
     */
    autoStart() {
        console.log('🔍 チュートリアル自動開始チェック中...');

        // 登録済みチュートリアルをチェック
        for (const [name, config] of this.tutorials) {
            // トリガー条件をチェック
            const shouldStart = this.checkTrigger(config.trigger);

            if (shouldStart) {
                console.log(`🎬 チュートリアル開始: ${name}`);
                this.start(name);
                return; // 1つだけ実行
            }
        }

        console.log('ℹ️ 開始条件に一致するチュートリアルはありません');
    }

    /**
     * トリガー条件をチェック
     */
    checkTrigger(trigger) {
        // 必須フラグがあるか
        if (trigger.requireFlag) {
            const flags = Array.isArray(trigger.requireFlag)
                ? trigger.requireFlag
                : [trigger.requireFlag];

            const hasRequired = flags.every(flag => this.hasFlag(flag));
            if (!hasRequired) return false;
        }

        // 禁止フラグがないか
        if (trigger.forbidFlag) {
            const flags = Array.isArray(trigger.forbidFlag)
                ? trigger.forbidFlag
                : [trigger.forbidFlag];

            const hasForbidden = flags.some(flag => this.hasFlag(flag));
            if (hasForbidden) return false;
        }

        // カスタム条件
        if (trigger.condition && typeof trigger.condition === 'function') {
            return trigger.condition();
        }

        return true;
    }

    /**
     * チュートリアルを開始
     */
    start(name) {
        const config = this.tutorials.get(name);
        if (!config) {
            console.error(`❌ チュートリアルが見つかりません: ${name}`);
            return;
        }

        // 既に実行中の場合はスキップ
        if (this.activeTutorial) {
            console.warn('⚠️ 既にチュートリアル実行中です');
            return;
        }

        this.activeTutorial = name;

        // tutorialOverlayを初期化
        if (!window.tutorialOverlay) {
            console.error('❌ tutorialOverlayが見つかりません');
            return;
        }

        // オプションを準備
        const options = {
            onComplete: () => {
                console.log(`🎉 チュートリアル完了: ${name}`);

                // 完了フラグを設定
                if (config.onComplete) {
                    config.onComplete();
                }

                // クリーンアップ
                if (window.tutorialHelper) {
                    window.tutorialHelper.cleanup();
                }

                this.activeTutorial = null;
            },

            onSkip: () => {
                console.log(`⏭️ チュートリアルスキップ: ${name}`);

                // スキップ処理
                if (config.onSkip) {
                    config.onSkip();
                }

                // クリーンアップ
                if (window.tutorialHelper) {
                    window.tutorialHelper.cleanup();
                }

                this.activeTutorial = null;
                return true;
            }
        };

        // ステップを取得（関数の場合は実行）
        const steps = typeof config.steps === 'function'
            ? config.steps()
            : config.steps;

        // チュートリアル開始
        tutorialOverlay.init(steps, options);
    }

    /**
     * チュートリアルを強制開始（デバッグ用）
     */
    forceStart(name) {
        console.log(`🚀 強制開始: ${name}`);
        this.start(name);
    }

    // ========================================
    // デバッグ用
    // ========================================

    /**
     * 状態をコンソールに表示
     */
    showStatus() {
        const phase = this.getCurrentPhase();
        const progress = this.getProgress();
        const nextFlag = this.getNextFlag();
        const flags = this.getFlagStatus();

        console.log('📊 チュートリアル状態:');
        console.log(`  現在のフェーズ: ${phase}`);
        console.log(`  進行率: ${progress}%`);
        console.log(`  次のフラグ: ${nextFlag || '完了'}`);
        console.log('  フラグ一覧:');
        console.table(flags);
    }

    /**
     * 特定のフェーズにジャンプ（デバッグ用）
     */
    jumpToPhase(phaseName) {
        this.clearAllFlags();

        const phaseMap = {
            'seikai': [this.FLAGS.START],
            'seikai_save': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE],
            'seikai_list': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED],
            'fuseikai': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED, this.FLAGS.FUSEIKAI_CREATE],
            'fuseikai_save': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED, this.FLAGS.FUSEIKAI_CREATE, this.FLAGS.FUSEIKAI_SAVE],
            'mondai': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED, this.FLAGS.FUSEIKAI_CREATE, this.FLAGS.FUSEIKAI_SAVE, this.FLAGS.FUSEIKAI_SAVED, this.FLAGS.MONDAI_CREATE],
            'algorithm': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED, this.FLAGS.FUSEIKAI_CREATE, this.FLAGS.FUSEIKAI_SAVE, this.FLAGS.FUSEIKAI_SAVED, this.FLAGS.MONDAI_CREATE, this.FLAGS.MONDAI_CREATED],
            'test': [this.FLAGS.START, this.FLAGS.SEIKAI_SAVE, this.FLAGS.SEIKAI_SAVED, this.FLAGS.FUSEIKAI_CREATE, this.FLAGS.FUSEIKAI_SAVE, this.FLAGS.FUSEIKAI_SAVED, this.FLAGS.MONDAI_CREATE, this.FLAGS.MONDAI_CREATED, this.FLAGS.ALGORITHM_SAVED]
        };

        const flags = phaseMap[phaseName];
        if (!flags) {
            console.error(`❌ 不明なフェーズ: ${phaseName}`);
            console.log('利用可能なフェーズ:', Object.keys(phaseMap));
            return;
        }

        flags.forEach(flag => this.setFlag(flag));
        console.log(`✅ ${phaseName}フェーズにジャンプしました`);
        console.log('ページをリロードしてください: location.reload()');
    }

    /**
     * 登録済みチュートリアル一覧を表示
     */
    listTutorials() {
        console.log('📚 登録済みチュートリアル:');
        this.tutorials.forEach((config, name) => {
            console.log(`  - ${name}`);
        });
    }
}

// グローバルインスタンスを作成
window.tutorialManager = new TutorialManager();

// デバッグ用のグローバル関数
window.showTutorialStatus = function () {
    tutorialManager.showStatus();
};

window.jumpToPhase = function (phaseName) {
    tutorialManager.jumpToPhase(phaseName);
};

console.log('🔧 TutorialManager loaded');
