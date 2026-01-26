// 共通ナビゲーション・タブ切替用JS
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    var tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(function(tab){
      tab.addEventListener('click', function(e){
        e.preventDefault();
        tabs.forEach(function(t){
          t.classList.remove('active');
          t.setAttribute('aria-pressed','false');
        });
        this.classList.add('active');
        this.setAttribute('aria-pressed','true');
        // タブごとの遷移
        if (this.id === 'tab-system') {
          window.location.href = '/accounts/system/choice';
        } else if (this.id === 'tab-algorithm') {
          window.location.href = '/accounts/block/choice';
        }
        // 他タブは見た目切替のみ
      });
    });
  });
})();
