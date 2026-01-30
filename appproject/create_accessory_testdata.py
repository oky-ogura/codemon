"""
アクセサリーシステムのテストデータを作成するスクリプト
"""
import os
import sys
import django

# Djangoの設定を読み込む
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
django.setup()

from codemon.models import Accessory, UserCoin
from accounts.models import Account

def create_test_data():
    """テストデータを作成"""
    print("アクセサリーマスターデータを作成中...")
    
    # アクセサリーマスターデータを作成
    accessories = [
        # 花
        {
            'name': 'サンフラワー・ドッグ',
            'category': 'flower',
            'css_class': 'flower.inu',
            'description': '元気いっぱい！友情がぱっとさく',
            'unlock_coins': 100,
        },
        {
            'name': 'ピュアフラワー・ラビット',
            'category': 'flower',
            'css_class': 'flower.usagi',
            'description': 'こわくても、一歩ふみだすゆうき',
            'unlock_coins': 100,
        },
        {
            'name': 'ウィンクフラワー・フォックス',
            'category': 'flower',
            'css_class': 'flower.kitsune',
            'description': 'からかい上手なスマイル付き',
            'unlock_coins': 100,
        },
        {
            'name': 'クールブルーム・キャット',
            'category': 'flower',
            'css_class': 'flower.neko',
            'description': '気分でさく、それがネコ',
            'unlock_coins': 100,
        },
        {
            'name': 'おひるねフラワー・パンダ',
            'category': 'flower',
            'css_class': 'flower.panda',
            'description': 'のんびり心に花ひらく',
            'unlock_coins': 100,
        },
        {
            'name': 'ナレッジフラワー・フクロウ',
            'category': 'flower',
            'css_class': 'flower.fukurou',
            'description': '知恵がすっと身につく',
            'unlock_coins': 100,
        },
        {
            'name': 'ヒーローフラワー・リス',
            'category': 'flower',
            'css_class': 'flower.risu',
            'description': 'せいぎの心がまんかい！',
            'unlock_coins': 100,
        },
        {
            'name': 'ノーブルフラワー・アルパカ',
            'category': 'flower',
            'css_class': 'flower.alpaca',
            'description': '気品とやさしさのいちりん',
            'unlock_coins': 100,
        },
        # 眼鏡
        {
            'name': 'ファイトグラス・ドッグ',
            'category': 'glasses',
            'css_class': 'glasses.inu',
            'description': '気合いとこんじょう、しかいりょうこう！',
            'unlock_coins': 100,
        },
        {
            'name': 'まじめメガネ・ラビット',
            'category': 'glasses',
            'css_class': 'glasses.usagi',
            'description': 'コツコツ努力のみかた',
            'unlock_coins': 100,
        },
        {
            'name': 'ニヤリグラス・フォックス',
            'category': 'glasses',
            'css_class': 'glasses.kitsune',
            'description': '全部お見通し？',
            'unlock_coins': 100,
        },
        {
            'name': 'マイペースグラス・キャット',
            'category': 'glasses',
            'css_class': 'glasses.neko',
            'description': '見たいものだけ見る',
            'unlock_coins': 100,
        },
        {
            'name': 'ゆるゆるグラス・パンダ',
            'category': 'glasses',
            'css_class': 'glasses.panda',
            'description': 'ぼーっとしてても大丈夫',
            'unlock_coins': 100,
        },
        {
            'name': 'ティーチャーグラス・フクロウ',
            'category': 'glasses',
            'css_class': 'glasses.fukurou',
            'description': '学びのプロフェッショナル',
            'unlock_coins': 100,
        },
        {
            'name': 'ツンデレグラス・リス',
            'category': 'glasses',
            'css_class': 'glasses.risu',
            'description': '別に助けたいわけじゃ…',
            'unlock_coins': 100,
        },
        {
            'name': 'エレガントグラス・アルパカ',
            'category': 'glasses',
            'css_class': 'glasses.alpaca',
            'description': 'できる大人のたしなみ',
            'unlock_coins': 100,
        },
        # リボン
        {
            'name': 'フレンドリボン・ドッグ',
            'category': 'ribbon',
            'css_class': 'ribbon.inu',
            'description': 'ともだちパワーけっそく！',
            'unlock_coins': 100,
        },
        {
            'name': 'ドキドキリボン・ラビット',
            'category': 'ribbon',
            'css_class': 'ribbon.usagi',
            'description': 'ドキド勇気をきゅっと結んで',
            'unlock_coins': 100,
        },
        {
            'name': 'いたずらリボン・フォックス',
            'category': 'ribbon',
            'css_class': 'ribbon.kitsune',
            'description': '油断すると結ばれる？',
            'unlock_coins': 100,
        },
        {
            'name': 'きまぐれリボン・キャット',
            'category': 'ribbon',
            'css_class': 'ribbon.neko',
            'description': '今日はつける気分',
            'unlock_coins': 100,
        },
        {
            'name': 'ふわふわリボン・パンダ',
            'category': 'ribbon',
            'css_class': 'ribbon.panda',
            'description': 'ねむくなる可愛さ',
            'unlock_coins': 100,
        },
        {
            'name': 'ロジックリボン・フクロウ',
            'category': 'ribbon',
            'css_class': 'ribbon.fukurou',
            'description': '考えが整理される',
            'unlock_coins': 100,
        },
        {
            'name': 'せいぎリボン・リス',
            'category': 'ribbon',
            'css_class': 'ribbon.risu',
            'description': '守ると決めたら全力で！',
            'unlock_coins': 100,
        },
        {
            'name': 'エレガントグラス・アルパカ',
            'category': 'ribbon',
            'css_class': 'ribbon.alpaca',
            'description': 'できる大人のたしなみ',
            'unlock_coins': 100,
        },
        {
            'name': 'レディリボン・アルパカ',
            'category': 'ribbon',
            'css_class': 'ribbon.alpaca',
            'description': '上品さは基本装備',
            'unlock_coins': 100,
        },
        # 星
        {
            'name': 'ヒーロースター・ドッグ',
            'category': 'star',
            'css_class': 'star.inu',
            'description': '輝く友情のしるし',
            'unlock_coins': 100,
        },
        {
            'name': 'スモールスター・ラビット',
            'category': 'star',
            'css_class': 'star.usagi',
            'description': '小さなひかりも大切に',
            'unlock_coins': 100,
        },
        {
            'name': 'トリックスター・フォックス',
            'category': 'star',
            'css_class': 'star.kitsune',
            'description': 'きらりとひにくが光る',
            'unlock_coins': 100,
        },
        {
            'name': 'ナイトスター・キャット',
            'category': 'star',
            'css_class': 'star.neko',
            'description': '静かにかがやく',
            'unlock_coins': 100,
        },
        {
            'name': 'おやすみスター・パンダ',
            'category': 'star',
            'css_class': 'star.panda',
            'description': '夢の中でもきらきら',
            'unlock_coins': 100,
        },
        {
            'name': 'ウィズダムスター・フクロウ',
            'category': 'star',
            'css_class': 'star.fukurou',
            'description': 'ちしきの星がみちびく',
            'unlock_coins': 100,
        },
        {
            'name': 'ジャスティススター・リス',
            'category': 'star',
            'css_class': 'star.risu',
            'description': '正義は負けない',
            'unlock_coins': 100,
        },
        {
            'name': 'ロイヤルスター・アルパカ',
            'category': 'star',
            'css_class': 'star.alpaca',
            'description': '違いが光る',
            'unlock_coins': 100,
        },
        # 帽子
        {
            'name': 'チャレンジハット・ドッグ',
            'category': 'hat',
            'css_class': 'hat.inu',
            'description': '前向き全開！',
            'unlock_coins': 100,
        },
        {
            'name': 'セーフティハット・ラビット',
            'category': 'hat',
            'css_class': 'hat.usagi',
            'description': '安心感ばっちり',
            'unlock_coins': 100,
        },
        {
            'name': 'トリックハット・フォックス',
            'category': 'hat',
            'css_class': 'hat.kitsune',
            'description': '何が出るかはヒミツ',
            'unlock_coins': 100,
        },
        {
            'name': 'フリーダムハット・キャット',
            'category': 'hat',
            'css_class': 'hat.neko',
            'description': '縛られないスタイル',
            'unlock_coins': 100,
        },
        {
            'name': 'ロイヤルスター・アルパカ',
            'category': 'hat',
            'css_class': 'hat.alpaca',
            'description': '違いが光る',
            'unlock_coins': 100,
        },
        {
            'name': 'のんびりハット・パンダ',
            'category': 'hat',
            'css_class': 'hat.panda',
            'description': 'かぶった瞬間お昼寝モード',
            'unlock_coins': 100,
        },
        {
            'name': 'プロフェッサーハット・フクロウ',
            'category': 'hat',
            'css_class': 'hat.fukurou',
            'description': '先生の本気',
            'unlock_coins': 100,
        },
        {
            'name': 'ガーディアンハット・リス',
            'category': 'hat',
            'css_class': 'hat.risu',
            'description': '守るかくごはばんぜん',
            'unlock_coins': 100,
        },
        {
            'name': 'マダムハット・アルパカ',
            'category': 'hat',
            'css_class': 'hat.alpaca',
            'description': 'たよれるあねごのふうかく',
            'unlock_coins': 100,
        },
        # 王冠
        {
            'name': 'ブレイブクラウン・ドッグ',
            'category': 'crown',
            'css_class': 'crown.inu',
            'description': '友情の王者',
            'unlock_coins': 100,
        },
        {
            'name': 'スモールクラウン・ラビット',
            'category': 'crown',
            'css_class': 'crown.usagi',
            'description': 'がんばったあかし',
            'unlock_coins': 100,
        },
        {
            'name': 'シャドウクラウン・フォックス',
            'category': 'crown',
            'css_class': 'crown.kitsune',
            'description': 'うらからしはい？',
            'unlock_coins': 100,
        },
        {
            'name': 'クールクラウン・キャット',
            'category': 'crown',
            'css_class': 'crown.neko',
            'description': '王でもマイペース',
            'unlock_coins': 100,
            'use_image': True,
            'image_path': 'codemon/images/accessories/crown_neko.png',
        },
        {
            'name': 'リラックスクラウン・パンダ',
            'category': 'crown',
            'css_class': 'crown.panda',
            'description': 'ねながら王様',
            'unlock_coins': 100,
        },
        {
            'name': 'マスタークラウン・フクロウ',
            'category': 'crown',
            'css_class': 'crown.fukurou',
            'description': '知のちょうてん',
            'unlock_coins': 100,
        },
        {
            'name': 'ヒーロークラウン・リス',
            'category': 'crown',
            'css_class': 'crown.risu',
            'description': 'せいぎのリーダー',
            'unlock_coins': 100,
        },
        {
            'name': 'クイーンクラウン・アルパカ',
            'category': 'crown',
            'css_class': 'crown.alpaca',
            'description': '気品と実力のしょうちょう',
            'unlock_coins': 100,
        },


    ]
    
    created_count = 0
    for acc_data in accessories:
        accessory, created = Accessory.objects.get_or_create(
            name=acc_data['name'],
            defaults=acc_data
        )
        if created:
            created_count += 1
            print(f"✓ {accessory.name} を作成しました")
        else:
            print(f"- {accessory.name} は既に存在します")
    
    print(f"\nアクセサリーマスターデータ作成完了: {created_count}件作成")
    
    # 全ユーザーに初期コインを付与
    print("\n全ユーザーに初期コインを付与中...")
    users = Account.objects.all()
    coin_count = 0
    
    for user in users:
        user_coin, created = UserCoin.objects.get_or_create(
            user=user,
            defaults={
                'balance': 10000,  # 初期コイン1000枚
                'total_earned': 10000,
            }
        )
        if created:
            coin_count += 1
            print(f"✓ {user.user_name} に1000コインを付与しました")
        else:
            print(f"- {user.user_name} は既にコインを持っています（残高: {user_coin.balance}）")
    
    print(f"\nコイン付与完了: {coin_count}名に付与")
    
    print("\n" + "="*50)
    print("テストデータの作成が完了しました！")
    print("="*50)
    print(f"\n作成されたアクセサリー: {Accessory.objects.count()}種類")
    print(f"コインを持つユーザー: {UserCoin.objects.count()}名")
    print("\nアクセサリーショップにアクセスして確認してください。")
    print("URL: http://127.0.0.1:8000/codemon/accessories/")

if __name__ == '__main__':
    create_test_data()
