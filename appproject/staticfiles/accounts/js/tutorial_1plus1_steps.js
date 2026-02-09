/**
 * 「1+1=?」チュートリアルの31ステップデータ
 * 小学生向けプログラミングチュートリアル
 */

console.log('📖 tutorial_1plus1_steps.js 読み込み開始');

const TUTORIAL_1PLUS1_STEPS = [
  // ステップ0: ようこそ
  {
    step: 0,
    title: 'ようこそ！',
    content: `
      <h3>「１＋１は？」のクイズをつくろう！</h3>
      <p>このチュートリアルでは、かんたんなクイズをつくる方法を学びます。</p>
      <p>ボタンを押して、ステップごとに進めていきましょう。</p>
      <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 10px;">
        <strong>📚 学べること:</strong>
        <ul style="margin-top: 10px;">
          <li>チェックボックスの作り方</li>
          <li>ボタンの作り方</li>
          <li>アルゴリズム（自動で動く仕組み）の作り方</li>
        </ul>
      </div>
    `
  },

  // ステップ1: システムを作る
  {
    step: 1,
    title: 'ステップ1: 新しいシステムを作ろう',
    content: `
      <h3>「次へ」を押そう</h3>
      <p>まず、クイズの画面を作ります。</p>
      <p>画面の下にある<strong class="highlight">「次へ」</strong>ボタンを押してください。</p>
      <p>次のページに移動して、チュートリアルが続きます。</p>
      <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px;">
        💡 <strong>ポイント:</strong> ページが変わっても、このチュートリアルは続きます！
      </div>
    `
  },

  // ステップ2: システム名を入力
  {
    step: 2,
    title: 'ステップ2: システム名を入力しよう',
    content: `
      <h3>「1+1クイズ」と入力しよう</h3>
      <p>システム作成画面が開きました。</p>
      <p><strong>システム名</strong>の入力欄に<strong class="highlight">「1+1クイズ」</strong>と入力してください。</p>
      <div style="margin-top: 15px; padding: 12px; background: #e7f3ff; border-radius: 5px;">
        <strong>📝 システムとは？</strong><br>
        あなたが作るプログラムの画面のことです
      </div>
    `
  },

  // ステップ3: 詳細説明を入力
  {
    step: 3,
    title: 'ステップ3: 詳細を入力しよう',
    content: `
      <h3>「1+1の答えを選ぶクイズです」と入力しよう</h3>
      <p><strong>詳細説明</strong>の入力欄に、上記の文を入力してください。</p>
      <p>入力できたら、<strong class="highlight">「作成」</strong>ボタンを押します。</p>
      <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px;">
        💡 <strong>ヒント:</strong> 詳細説明は、あとで見たときに何のシステムか分かるようにするためのものです
      </div>
    `
  },

  // ステップ4以降は今後の実装で使用
  {
    step: 4,
    title: 'ステップ4: システムが作成されました！',
    content: `
      <h3>おめでとうございます！</h3>
      <p>システムが作成されました。</p>
      <p>これで、あなた専用の画面ができました！</p>
      <div style="margin-top: 20px; padding: 15px; background: #f0f8ff; border-radius: 10px;">
        <strong>📚 ここまでのまとめ:</strong>
        <ul style="margin-top: 10px;">
          <li>システム（画面）を作る方法を学びました</li>
          <li>システム名と詳細を入力する方法を学びました</li>
        </ul>
      </div>
      <p style="margin-top: 20px;">チュートリアルはここまでです。「完了」を押して終了しましょう。</p>
      <div style="margin-top: 15px; padding: 12px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 5px;">
        ✨ <strong>次のステップ:</strong> 作成したシステムに、ボタンやチェックボックスを追加してみましょう！
      </div>
    `
  }
];

console.log(`✅ チュートリアルステップデータ読み込み完了 (全${TUTORIAL_1PLUS1_STEPS.length}ステップ)`);

// グローバルに公開
if (typeof window !== 'undefined') {
  window.TUTORIAL_1PLUS1_STEPS = TUTORIAL_1PLUS1_STEPS;
}
    content: `
      <h3>選択肢を「1」「2」「3」に変えよう</h3>
      <p>画面にチェックボックスが作られました！</p>
      <p>それぞれの選択肢をクリックして、以下のように変えましょう：</p>
      <ul style="line-height: 2;">
        <li>「項目 1」→ <strong class="highlight">「1」</strong></li>
        <li>「項目 2」→ <strong class="highlight">「2」</strong></li>
        <li>「項目 3」→ <strong class="highlight">「3」</strong></li>
      </ul>
    `
  },

  // ステップ6: ボタンを追加
  {
    step: 6,
    title: 'ステップ6: ボタンを追加しよう',
    content: `
      <h3>「ボタン追加」を押そう</h3>
      <p>答えをチェックするためのボタンを作ります。</p>
      <p><strong class="highlight">「ボタン追加」</strong>のボタンを押してください。</p>
    `
  },

  // ステップ7: ボタンの設定
  {
    step: 7,
    title: 'ステップ7: ボタンを作ろう',
    content: `
      <h3>そのまま「作成」を押そう</h3>
      <p>ボタンの設定画面が開きました。</p>
      <p>今回は設定を変えずに、<strong class="highlight">「作成」</strong>ボタンを押してください。</p>
    `
  },

  // ステップ8: ボタンを右クリック
  {
    step: 8,
    title: 'ステップ8: ボタンを右クリックしよう',
    content: `
      <h3>作ったボタンを右クリックしよう</h3>
      <p>ボタンが作られました！</p>
      <p>このボタンを<strong class="highlight">右クリック</strong>してください。</p>
      <div style="margin-top: 15px; padding: 12px; background: #e7f3ff; border-radius: 5px;">
        <strong>🖱️ 右クリックとは？</strong><br>
        マウスの右側のボタンを押すことです
      </div>
    `
  },

  // ステップ9: アルゴリズムを新規作成
  {
    step: 9,
    title: 'ステップ9: アルゴリズムを作ろう',
    content: `
      <h3>「アルゴリズムを新規作成」を選ぼう</h3>
      <p>メニューが開きました。</p>
      <p><strong class="highlight">「アルゴリズムを新規作成」</strong>を押してください。</p>
      <div style="margin-top: 15px; padding: 12px; background: #e7f3ff; border-radius: 5px;">
        <strong>🤖 アルゴリズムとは？</strong><br>
        自動で動く仕組みのことです。「もし○○なら△△する」という命令を作れます
      </div>
    `
  },

  // ステップ10-27: Blocklyでのアルゴリズム作成（簡略化）
  {
    step: 10,
    title: 'ステップ10: ブロックを使おう',
    content: `
      <h3>「もし　システム」ブロックを使おう</h3>
      <p>ブロックを組み合わせてプログラムを作ります。</p>
      <p>左のメニューから<strong class="highlight">「もし　システム」</strong>ブロックを見つけて、画面の真ん中にドラッグしてください。</p>
    `
  },

  {
    step: 11,
    title: 'ステップ11: ブロックを置こう',
    content: `
      <h3>ブロックを作業スペースに置こう</h3>
      <p>ブロックを右側の白い作業スペースに置きます。</p>
      <p>マウスのボタンを離して、ブロックを置いてください。</p>
    `
  },

  {
    step: 12,
    title: 'ステップ12: チェックボックスを選ぼう',
    content: `
      <h3>ブロックの設定をしよう (1/6)</h3>
      <p>ブロックの中の<strong class="highlight">最初のメニュー</strong>を押します。</p>
      <p>出てきたメニューから<strong class="highlight">「１＋１は？」</strong>を選んでください。</p>
    `
  },

  {
    step: 13,
    title: 'ステップ13: 条件を選ぼう',
    content: `
      <h3>ブロックの設定をしよう (2/6)</h3>
      <p><strong class="highlight">2番目のメニュー</strong>を押します。</p>
      <p><strong class="highlight">「が選ばれていたら」</strong>を選んでください。</p>
    `
  },

  {
    step: 14,
    title: 'ステップ14: 答えを選ぼう',
    content: `
      <h3>ブロックの設定をしよう (3/6)</h3>
      <p><strong class="highlight">3番目のメニュー</strong>を押します。</p>
      <p><strong class="highlight">「2」</strong>を選んでください。</p>
      <div style="margin-top: 15px; padding: 12px; background: #d4edda; border-radius: 5px;">
        ✅ <strong>ポイント:</strong> 「1+1」の答えは「2」なので、「2」が選ばれたら正解です！
      </div>
    `
  },

  {
    step: 15,
    title: 'ステップ15: 正解の画面を選ぼう',
    content: `
      <h3>ブロックの設定をしよう (4/6)</h3>
      <p>ブロックの下の方にある<strong class="highlight">「システムをひょうじ」</strong>の横のメニューを押します。</p>
      <p><strong class="highlight">「正解」</strong>のシステムを選んでください。</p>
    `
  },

  {
    step: 16,
    title: 'ステップ16: 「でなければ」を使おう',
    content: `
      <h3>ブロックの設定をしよう (5/6)</h3>
      <p>ブロックの一番下に<strong class="highlight">「でなければ」</strong>という部分があります。</p>
      <p>その横のメニューから<strong class="highlight">「不正解」</strong>のシステムを選んでください。</p>
      <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-radius: 5px;">
        💡 <strong>意味:</strong> 「2」以外が選ばれたら、不正解の画面を表示します
      </div>
    `
  },

  {
    step: 17,
    title: 'ステップ17: 完成！',
    content: `
      <h3>アルゴリズムができました！</h3>
      <p>これで、答えをチェックする仕組みができました。</p>
      <p><strong>まとめ:</strong></p>
      <ul style="line-height: 2;">
        <li>「2」を選んだら → 正解の画面</li>
        <li>それ以外を選んだら → 不正解の画面</li>
      </ul>
    `
  },

  {
    step: 18,
    title: 'ステップ18: 名前を付けよう (1/3)',
    content: `
      <h3>アルゴリズムに名前を付けよう</h3>
      <p>作ったアルゴリズムを保存します。</p>
      <p>画面の上の方にある<strong class="highlight">「アルゴリズムそうさ」</strong>ボタンを押してください。</p>
    `
  },

  {
    step: 19,
    title: 'ステップ19: 保存を選ぼう (2/3)',
    content: `
      <h3>「ほぞん」を選ぼう</h3>
      <p>メニューが開きました。</p>
      <p><strong class="highlight">「ほぞん」</strong>を押してください。</p>
    `
  },

  {
    step: 20,
    title: 'ステップ20: 名前を入力しよう (3/3)',
    content: `
      <h3>名前を入力して保存しよう</h3>
      <p>アルゴリズム名を入力する欄が出てきます。</p>
      <p>好きな名前（例：<strong>「こたえチェック」</strong>）を入力して、<strong class="highlight">「ほぞん」</strong>ボタンを押してください。</p>
    `
  },

  // ステップ21-27: システムに戻る
  {
    step: 21,
    title: 'ステップ21: 保存完了！',
    content: `
      <h3>アルゴリズムが保存されました！</h3>
      <p>これで、ボタンを押したときの動きが設定できました。</p>
      <p>次は、実際に動かしてみましょう。</p>
      <div style="margin-top: 15px; padding: 12px; background: #d4edda; border-radius: 5px;">
        ✅ <strong>できたこと:</strong> クイズの仕組みが完成しました！
      </div>
    `
  },

  {
    step: 22,
    title: 'ステップ22: システム画面に戻ろう',
    content: `
      <h3>システムの画面に戻ろう</h3>
      <p>画面の左上にある<strong class="highlight">「システム」</strong>タブを押してください。</p>
      <p>作ったクイズの画面に戻ります。</p>
    `
  },

  {
    step: 23,
    title: 'ステップ23: システムを選ぼう',
    content: `
      <h3>作ったシステムを開こう</h3>
      <p><strong class="highlight">「つくったものをみる」</strong>ボタンを押して、作ったシステムを選んでください。</p>
    `
  },

  // ステップ24-27: テスト実行
  {
    step: 24,
    title: 'ステップ24: 間違えてみよう',
    content: `
      <h3>わざと間違えてみよう</h3>
      <p>まず、わざと<strong>「1」か「3」</strong>を選んでみましょう。</p>
      <p>そして、<strong class="highlight">「ボタン」</strong>を押してください。</p>
      <p>どうなるかな？</p>
    `
  },

  {
    step: 25,
    title: 'ステップ25: 不正解！',
    content: `
      <h3>「ざんねん...もういちど！」と表示されたね</h3>
      <p>これが<strong>「不正解」</strong>の画面です。</p>
      <p>間違えると、この画面が表示されるようにプログラムされています。</p>
      <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-radius: 5px;">
        💡 <strong>確認:</strong> アルゴリズムが正しく動いていますね！
      </div>
    `
  },

  {
    step: 26,
    title: 'ステップ26: 正解してみよう',
    content: `
      <h3>今度は正解を選ぼう</h3>
      <p>もう一度クイズの画面に戻って、今度は<strong class="highlight">「2」</strong>を選んでください。</p>
      <p>そして、<strong>「ボタン」</strong>を押してみましょう。</p>
    `
  },

  {
    step: 27,
    title: 'ステップ27: 正解！',
    content: `
      <h3>「せいかい！」と表示されたね</h3>
      <p>これが<strong>「正解」</strong>の画面です。</p>
      <p>正しい答えを選ぶと、この画面が表示されます。</p>
      <div style="margin-top: 15px; padding: 12px; background: #d4edda; border-radius: 5px;">
        🎉 <strong>すごい!</strong> プログラムが完璧に動いています！
      </div>
    `
  },

  // ステップ28-30: システム保存
  {
    step: 28,
    title: 'ステップ28: システムを保存しよう (1/3)',
    content: `
      <h3>作ったクイズを保存しよう</h3>
      <p>最初に作ったシステムの画面に戻ります。</p>
      <p>画面の上にある<strong class="highlight">「システム名」</strong>の欄に名前を入力してください。</p>
      <p>例: <strong>「１＋１クイズ」</strong></p>
    `
  },

  {
    step: 29,
    title: 'ステップ29: システムを保存しよう (2/3)',
    content: `
      <h3>説明も書いてみよう</h3>
      <p><strong class="highlight">「システムせつめい」</strong>の欄にも、クイズの説明を書いてみましょう。</p>
      <p>例: <strong>「1+1の答えを選ぶクイズです」</strong></p>
    `
  },

  {
    step: 30,
    title: 'ステップ30: システムを保存しよう (3/3)',
    content: `
      <h3>保存ボタンを押そう</h3>
      <p>最後に、<strong class="highlight">「ほぞん」</strong>ボタンを押してください。</p>
      <p>これで、作ったクイズが保存されます！</p>
    `
  },

  // ステップ31: 完了
  {
    step: 31,
    title: 'チュートリアル完了！🎉',
    content: `
      <h2 style="text-align: center; color: #28a745;">おめでとうございます！</h2>
      <div style="text-align: center; margin: 20px 0;">
        <div style="font-size: 80px;">🎊</div>
      </div>
      <h3>チュートリアルをクリアしました！</h3>
      <p>あなたは以下のことができるようになりました：</p>
      <ul style="line-height: 2.5;">
        <li>✅ チェックボックスを作る</li>
        <li>✅ ボタンを作る</li>
        <li>✅ アルゴリズム（自動で動く仕組み）を作る</li>
        <li>✅ 条件分岐（もし～なら）を使う</li>
        <li>✅ システムを保存する</li>
      </ul>
      <div style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; text-align: center;">
        <strong style="font-size: 18px;">🌟 これからも、いろいろなプログラムを作ってみてね！</strong>
      </div>
    `
  }
];

console.log('✅ tutorial_1plus1_steps.js 読み込み完了:', TUTORIAL_1PLUS1_STEPS.length, 'ステップ');
