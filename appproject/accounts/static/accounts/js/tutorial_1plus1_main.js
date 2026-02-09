/**
 * 「1+1=?」チュートリアル メイン制御スクリプト
 * 複数ページにまたがるチュートリアルをLocalStorageで管理
 */

console.log('📖 tutorial_1plus1_main.js 読み込み開始');

(function() {
  'use strict';

  let currentStep = 0;
  const totalSteps = 4;
  const STORAGE_KEY = 'tutorial1plus1_step';
  const STORAGE_ACTIVE = 'tutorial1plus1_active';
  
  // DOM要素
  let modal, modalElement, overlay, titleElement, bodyElement, stepIndicator, progressFill;
  let btnPrev, btnNext, btnSkip, btnClose;

  /**
   * 初期化
   */
  function init() {
    // DOM要素の取得
    modalElement = document.getElementById('tutorial1plus1Modal');
    
    if (!modalElement) {
      console.warn('⚠️ チュートリアルモーダルが見つかりません（このページには不要）');
      return;
    }
    
    overlay = modalElement.querySelector('.tutorial-overlay');
    titleElement = document.getElementById('tutorialTitle');
    bodyElement = document.getElementById('tutorialBody');
    stepIndicator = document.getElementById('tutorialStepIndicator');
    progressFill = document.getElementById('tutorialProgressFill');
    
    btnPrev = document.getElementById('tutorialPrev');
    btnNext = document.getElementById('tutorialNext');
    btnSkip = document.getElementById('tutorialSkip');
    btnClose = document.getElementById('tutorialClose');

    // イベントリスナーの設定
    if (btnPrev) btnPrev.addEventListener('click', handlePrev);
    if (btnNext) btnNext.addEventListener('click', handleNext);
    if (btnSkip) btnSkip.addEventListener('click', handleClose);
    if (btnClose) btnClose.addEventListener('click', handleClose);
    if (overlay) overlay.addEventListener('click', handleClose);

    // チュートリアル進行中なら自動表示
    checkAndRestoreTutorial();

    console.log('✅ チュートリアル初期化完了');
  }

  /**
   * チュートリアル進行中かチェックし、必要なら自動表示
   */
  function checkAndRestoreTutorial() {
    const isActive = localStorage.getItem(STORAGE_ACTIVE);
    const savedStep = localStorage.getItem(STORAGE_KEY);
    
    if (isActive === 'true' && savedStep !== null) {
      const step = parseInt(savedStep, 10);
      console.log(`🔄 チュートリアル再開: ステップ ${step}`);
      currentStep = step;
      showModalWithoutReset();
    }
  }

  /**
   * モーダルを表示（新規開始）
   */
  function showModal() {
    if (!modalElement) {
      console.error('❌ チュートリアルモーダルが見つかりません');
      return;
    }

    // 新規開始
    currentStep = 0;
    saveProgress();
    
    // モーダル表示
    modalElement.style.display = 'flex';
    
    // 最初のステップを表示
    showStep(currentStep);
    
    // body のスクロールを無効化
    document.body.style.overflow = 'hidden';

    console.log('📖 チュートリアル開始');
  }

  /**
   * モーダルを表示（進行状況を保持）
   */
  function showModalWithoutReset() {
    if (!modalElement) {
      return;
    }
    
    // モーダル表示
    modalElement.style.display = 'flex';
    
    // 現在のステップを表示
    showStep(currentStep);
    
    // body のスクロールを無効化
    document.body.style.overflow = 'hidden';
  }

  /**
   * 進行状況を保存
   */
  function saveProgress() {
    localStorage.setItem(STORAGE_ACTIVE, 'true');
    localStorage.setItem(STORAGE_KEY, currentStep.toString());
  }

  /**
   * 進行状況をクリア
   */
  function clearProgress() {
    localStorage.removeItem(STORAGE_ACTIVE);
    localStorage.removeItem(STORAGE_KEY);
  }

  /**
   * モーダルを閉じる
   */
  function handleClose() {
    if (modalElement) {
      modalElement.style.display = 'none';
    }
    
    // body のスクロールを有効化
    document.body.style.overflow = '';
    
    // 進行状況をクリア
    clearProgress();
    
    console.log('📕 チュートリアル終了');
  }

  /**
   * 指定したステップを表示
   */
  function showStep(step) {
    // ステップ範囲チェック
    if (step < 0 || step > totalSteps) {
      console.warn(`⚠️ 無効なステップ: ${step}`);
      return;
    }

    currentStep = step;
    
    // 進行状況を保存
    saveProgress();

    // ステップデータの取得
    const stepData = TUTORIAL_1PLUS1_STEPS.find(s => s.step === step);
    
    if (!stepData) {
      console.error(`❌ ステップ ${step} のデータが見つかりません`);
      return;
    }

    // タイトルとコンテンツを更新
    if (titleElement) titleElement.textContent = stepData.title;
    if (bodyElement) {
      bodyElement.innerHTML = stepData.content;
      // コンテンツ更新後、スクロール位置をトップに
      bodyElement.scrollTop = 0;
    }

    // ステップインジケーター更新
    if (stepIndicator) {
      stepIndicator.textContent = `ステップ ${step} / ${totalSteps}`;
    }

    // プログレスバー更新
    if (progressFill) {
      const progress = (step / totalSteps) * 100;
      progressFill.style.width = `${progress}%`;
    }

    // ボタン表示制御
    updateButtons(step);

    console.log(`📄 ステップ ${step} 表示: ${stepData.title}`);
  }

  /**
   * ボタンの表示・テキスト更新
   */
  function updateButtons(step) {
    // 「戻る」ボタン
    if (btnPrev) {
      btnPrev.style.display = step > 0 ? 'flex' : 'none';
    }

    // 「次へ」ボタン
    if (btnNext) {
      if (step === totalSteps) {
        // 最終ステップ
        btnNext.innerHTML = '完了 <i class="fas fa-check"></i>';
      } else {
        btnNext.innerHTML = '次へ <i class="fas fa-arrow-right"></i>';
      }
    }

    // 「スキップ」ボタン（最終ステップでは非表示）
    if (btnSkip) {
      btnSkip.style.display = step === totalSteps ? 'none' : 'flex';
    }
  }

  /**
   * 「戻る」ボタン処理
   */
  function handlePrev() {
    if (currentStep > 0) {
      showStep(currentStep - 1);
    }
  }

  /**
   * 「次へ」ボタン処理
   */
  function handleNext() {
    // Step 1から2に進む時は、system/create ページに遷移
    if (currentStep === 1) {
      console.log('🚀 システム作成ページに遷移します');
      // Step 2に進めてから遷移
      currentStep = 2;
      saveProgress();
      window.location.href = '/accounts/system/create/';
      return;
    }
    
    if (currentStep < totalSteps) {
      showStep(currentStep + 1);
    } else {
      // 最終ステップで「完了」を押した場合
      handleComplete();
    }
  }

  /**
   * チュートリアル完了処理
   */
  function handleComplete() {
    console.log('🎉 チュートリアル完了！');
    
    // 進行状況をクリア
    clearProgress();
    
    // モーダルを閉じる
    handleClose();
    
    // TODO: 将来的にサーバーに完了通知を送る場合はここに実装
    // fetch('/api/tutorial/1plus1/complete/', { method: 'POST' });
  }

  /**
   * グローバルに公開する関数
   */
  window.showTutorial1Plus1Modal = function() {
    showModal();
  };

  // DOM読み込み完了後に初期化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

console.log('✅ tutorial_1plus1_main.js 読み込み完了');
