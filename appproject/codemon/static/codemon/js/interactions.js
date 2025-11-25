/**
 * Codemon インタラクション JavaScript
 * 小学生向けの楽しい演出とキーボード操作対応
 */

(function() {
  'use strict';

  // ==================== 初期化 ====================
  document.addEventListener('DOMContentLoaded', function() {
    initKeyboardNavigation();
    initButtonEffects();
    initCharacterInteractions();
    initSpeechBubbleEffects();
  });

  // ==================== キーボードナビゲーション ====================
  function initKeyboardNavigation() {
    // タブキーでフォーカス可能な要素を取得
    const focusableElements = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    focusableElements.forEach((element, index) => {
      // Enterキーでボタンをクリック
      element.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && element.tagName !== 'TEXTAREA') {
          e.preventDefault();
          element.click();
        }
      });

      // 矢印キーでの移動（オプション）
      element.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          const nextIndex = (index + 1) % focusableElements.length;
          focusableElements[nextIndex].focus();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          const prevIndex = (index - 1 + focusableElements.length) % focusableElements.length;
          focusableElements[prevIndex].focus();
        }
      });
    });

    // フォーカス時に楽しいエフェクト
    focusableElements.forEach(element => {
      element.addEventListener('focus', function() {
        this.classList.add('focused-element');
        playFocusSound(); // サウンドエフェクト（オプション）
      });

      element.addEventListener('blur', function() {
        this.classList.remove('focused-element');
      });
    });
  }

  // ==================== ボタンエフェクト ====================
  function initButtonEffects() {
    const buttons = document.querySelectorAll('.btn-custom');

    buttons.forEach(button => {
      // ホバー時のバウンス効果
      button.addEventListener('mouseenter', function() {
        this.classList.add('btn-bounce');
      });

      button.addEventListener('mouseleave', function() {
        this.classList.remove('btn-bounce');
      });

      // クリック時のリップルエフェクト
      button.addEventListener('click', function(e) {
        createRipple(e, this);
        playClickSound(); // サウンドエフェクト（オプション）
      });
    });
  }

  // リップルエフェクト作成
  function createRipple(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple-effect');

    element.appendChild(ripple);

    setTimeout(() => ripple.remove(), 600);
  }

  // ==================== キャラクターインタラクション ====================
  function initCharacterInteractions() {
    const character = document.querySelector('.character-image');
    if (!character) return;

    // キャラクターをクリックしたときの反応
    character.style.cursor = 'pointer';
    character.style.pointerEvents = 'auto';

    character.addEventListener('click', function() {
      this.classList.add('character-excited');
      setTimeout(() => {
        this.classList.remove('character-excited');
      }, 1000);

      // 吹き出しのメッセージを変更（オプション）
      showRandomMessage();
    });

    // マウスオーバーで少し動く
    character.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-50%) scale(1.05) rotate(2deg)';
    });

    character.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(-50%) scale(1) rotate(0deg)';
    });
  }

  // ==================== 吹き出しエフェクト ====================
  function initSpeechBubbleEffects() {
    const bubble = document.querySelector('.speech-bubble');
    if (!bubble) return;

    // 吹き出しをクリックすると新しいメッセージ
    bubble.style.cursor = 'pointer';
    bubble.addEventListener('click', function() {
      this.classList.add('bubble-pop');
      setTimeout(() => {
        this.classList.remove('bubble-pop');
      }, 500);
    });
  }

  // ランダムメッセージ表示
  function showRandomMessage() {
    const messages = [
      'がんばって！',
      'やったね！',
      'すごいね！',
      'たのしいね！',
      'いっしょにやろう！'
    ];

    const bubble = document.querySelector('.speech-bubble');
    if (bubble) {
      const randomMsg = messages[Math.floor(Math.random() * messages.length)];
      bubble.textContent = randomMsg;

      // 元のメッセージに戻す
      setTimeout(() => {
        bubble.textContent = bubble.dataset.originalText || randomMsg;
      }, 2000);
    }
  }

  // ==================== サウンドエフェクト（オプション） ====================
  function playFocusSound() {
    // 後でサウンドファイルを追加する場合
    // const audio = new Audio('/static/codemon/sounds/focus.mp3');
    // audio.volume = 0.3;
    // audio.play();
  }

  function playClickSound() {
    // 後でサウンドファイルを追加する場合
    // const audio = new Audio('/static/codemon/sounds/click.mp3');
    // audio.volume = 0.5;
    // audio.play();
  }

  // ==================== パーティクルエフェクト（将来の拡張用） ====================
  function createParticles(x, y) {
    const colors = ['#FFD700', '#FF69B4', '#87CEEB', '#98FB98'];
    const particleCount = 10;

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = x + 'px';
      particle.style.top = y + 'px';
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];

      document.body.appendChild(particle);

      // アニメーション後に削除
      setTimeout(() => particle.remove(), 1000);
    }
  }

  // ==================== ページ読み込み時のアニメーション ====================
  window.addEventListener('load', function() {
    const character = document.querySelector('.character-image');
    const bubble = document.querySelector('.speech-bubble');

    if (character) {
      character.style.opacity = '0';
      setTimeout(() => {
        character.style.transition = 'opacity 1s ease-in-out';
        character.style.opacity = '1';
      }, 300);
    }

    if (bubble) {
      bubble.style.opacity = '0';
      bubble.style.transform = 'translateY(-50%) scale(0.8)';
      setTimeout(() => {
        bubble.style.transition = 'all 0.5s ease-out';
        bubble.style.opacity = '1';
        bubble.style.transform = 'translateY(-50%) scale(1)';
      }, 600);
    }
  });

})();
