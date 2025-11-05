from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
 # password ハッシュ化はフォーム側で行うように変更しました
from .forms import TeacherSignupForm, StudentSignupForm
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from .models import Account
from django.conf import settings


# カスタムのパスワード再設定ビュー
class MyPasswordResetView(auth_views.PasswordResetView):
    """戻るボタンがログイン画面へ戻るように back_url をコンテキストに設定するビュー。

    リファラ（HTTP_REFERER）に `teacher_login` が含まれていれば教員ログインへ、
    それ以外は生徒ログインへ遷移する URL を設定します。
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = self.request.META.get('HTTP_REFERER', '')
        if 'teacher_login' in referer:
            back = reverse('teacher_login')
        else:
            back = reverse('student_login')
        context['back_url'] = back
        return context


def get_logged_account(request):
    """セッションまたは Django の request.user から Account を取得するヘルパー。

    返り値: Account オブジェクト または None
    """
    try:
        # まず Django の認証ユーザーに紐づく Account があれば使う
        if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
            email = getattr(request.user, 'email', None)
            if email:
                acc = Account.objects.filter(email=email).first()
                if acc:
                    return acc
        # セッションベースの認証フラグがあればそれを使う
        if request.session.get('is_account_authenticated'):
            uid = request.session.get('account_user_id')
            if uid is not None:
                return Account.objects.filter(user_id=uid).first()
    except Exception:
        return None
    return None


def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            # フォームの save() でパスワードのハッシュ化と基本フィールド設定を行う
            instance = form.save()
            # role（ユーザー種別）をフォームから受け取り、必要なら上書き
            role = request.POST.get('role', 'teacher')
            if role and role != instance.account_type:
                instance.account_type = role
                instance.save()
            # サインアップ直後に確認ページで入力内容を表示できるようセッションに保持
            try:
                request.session['pending_account_name'] = instance.user_name
                request.session['pending_account_email'] = instance.email
            except Exception:
                pass
            # 登録後は AI 外見設定へ遷移
            return redirect('ai_appearance')
    else:
        form = TeacherSignupForm()
    ages = range(3, 121)
    return render(request, 'accounts/t_signup.html', {'form': form, 'ages': ages})

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            # フォームの save() でハッシュ化と保存を行う
            instance = form.save()
            # サインアップ直後に確認ページで入力内容を表示できるようセッションに保持
            try:
                request.session['pending_account_name'] = instance.user_name
                request.session['pending_account_email'] = instance.email
            except Exception:
                pass
            # サインアップ後は AI 外見設定へ遷移
            return redirect('ai_appearance')
    else:
        form = StudentSignupForm()
    ages = range(3, 121)
    return render(request, 'accounts/s_signup.html', {'form': form, 'ages': ages})

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Account テーブルを使って認証（auth_user を利用しない）
        acc = Account.objects.filter(email=username).first() or Account.objects.filter(user_name=username).first()
        if acc and check_password(password, acc.password):
            # セッションにアカウント情報を保存
            request.session['is_account_authenticated'] = True
            request.session['account_user_id'] = acc.user_id
            request.session['account_email'] = acc.email
            request.session['account_user_name'] = acc.user_name
            # セッションを確実に保存
            request.session.modified = True
            try:
                request.session.save()
            except Exception:
                pass
            # 既定のアカウントダッシュボードへ遷移
            return redirect('account_dashboard')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'accounts/t_login.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Account テーブルを使って認証（auth_user を利用しない）
        acc = Account.objects.filter(email=username).first() or Account.objects.filter(user_name=username).first()
        if acc and check_password(password, acc.password):
            request.session['is_account_authenticated'] = True
            request.session['account_user_id'] = acc.user_id
            request.session['account_email'] = acc.email
            request.session['account_user_name'] = acc.user_name
            # セッションを確実に保存
            request.session.modified = True
            try:
                request.session.save()
            except Exception:
                pass
            return redirect('account_dashboard')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'accounts/s_login.html')

def user_logout(request):
    # セッション内のアカウント情報を削除してログアウト扱いにする
    for k in ['is_account_authenticated', 'account_user_id', 'account_email', 'account_user_name']:
        try:
            del request.session[k]
        except KeyError:
            pass
    # 標準の logout も呼んでおく（存在すれば安全）
    try:
        logout(request)
    except Exception:
        pass
    return redirect('home')  # ログアウト後の遷移先を適宜変更


def ai_appearance(request):
    """AI外見設定ページ（簡易版）。POSTで選択を受け取り、ログイン済みなら保存します。"""
    if request.method == 'POST':
        appearance = request.POST.get('appearance')
        try:
            from .models import AiConfig
            acc = get_logged_account(request)
            if acc is not None:
                cfg, _ = AiConfig.objects.get_or_create(user_id=acc.user_id)
                if appearance:
                    cfg.appearance = appearance
                    cfg.save()
        except Exception:
            pass
        # 外見選択後は初期設定画面へ遷移させる
        return redirect('ai_initial')

    appearances = ['triangle', 'round', 'robot']
    return render(request, 'accounts/ai_appearance.html', {'appearances': appearances})


def ai_initial_settings(request):
    """AI の初期設定（名前・性格・語尾など）を編集する画面"""
    from .models import AiConfig

    # デフォルトで利用する性格の候補
    personalities = ['元気', 'おとなしい', '優しい', '無口', '冷静']

    # POST は基本的に確認画面へ遷移するためのデータ送信に使い、
    # 確定保存は別のエンドポイントで行う（two-step flow）。
    if request.method == 'POST':
        # 確認画面から編集へ戻るケースではここに POST で値が入ります。
        ai_name = request.POST.get('ai_name', '')
        ai_personality = request.POST.get('ai_personality', '')
        ai_speech = request.POST.get('ai_speech', '')
        appearance = request.POST.get('appearance', '')

        # 保存せずにテンプレートへ渡すための一時オブジェクトを作る
        config = type('C', (), {
            'ai_name': ai_name or '',
            'ai_personality': ai_personality or '元気',
            'ai_speech': ai_speech or 'です',
            'appearance': appearance or 'triangle'
        })()

        return render(request, 'accounts/ai_initial_settings.html', {'config': config, 'personalities': personalities})

    # GET: 現在の設定を読み込む
    config = None
    try:
        acc = get_logged_account(request)
        if acc is not None:
            config = AiConfig.objects.filter(user_id=acc.user_id).first()
    except Exception:
        config = None

    if config is None:
        # テンプレートが期待するプロパティを持つダミーを用意
        config = type('C', (), {'ai_name':'','ai_personality':'元気','ai_speech':'です','appearance':'triangle'})()

    return render(request, 'accounts/ai_initial_settings.html', {'config': config, 'personalities': personalities})


def ai_initial_confirm(request):
    """受け取ったフォーム入力を保存せずに確認表示するビュー"""
    if request.method != 'POST':
        return redirect('ai_initial')

    ai_name = request.POST.get('ai_name', '')
    ai_personality = request.POST.get('ai_personality', '')
    ai_speech = request.POST.get('ai_speech', '')
    appearance = request.POST.get('appearance', '')

    return render(request, 'accounts/ai_settings_confirm.html', {
        'ai_name': ai_name,
        'ai_personality': ai_personality,
        'ai_speech': ai_speech,
        'appearance': appearance,
    })


def ai_initial_save(request):
    """実際に設定を保存するエンドポイント。確認ページからPOSTされる。"""
    from .models import AiConfig

    if request.method != 'POST':
        return redirect('ai_initial')

    ai_name = request.POST.get('ai_name', '')
    ai_personality = request.POST.get('ai_personality', '')
    ai_speech = request.POST.get('ai_speech', '')
    appearance = request.POST.get('appearance', '')

    try:
        acc = get_logged_account(request)
        if acc is not None:
            cfg, _ = AiConfig.objects.get_or_create(user_id=acc.user_id)
            if ai_name:
                cfg.ai_name = ai_name
            if ai_personality:
                cfg.ai_personality = ai_personality
            if ai_speech:
                cfg.ai_speech = ai_speech
            if appearance:
                cfg.appearance = appearance
            cfg.save()
    except Exception:
        pass

    return redirect('accounts_root')

def block_index(request):
    return render(request, 'block/index.html')

def system_index(request):
    return render(request, 'system/index.html')

# ブロック作成保存
def block_save(request):
    # 必要なら POST 処理をここに追加（保存処理など）
    return render(request, 'block/save.html')

# システム作成保存
def system_save(request):
    # 必要なら POST 処理をここに追加（保存処理など）
    return render(request, 'system/save.html')

# システム選択画面
def system_choice(request):
    return render(request, 'system/system_choice.html')

# システム新規作成画面（システム名、システムの詳細入力など）
def system_create(request):
    return render(request, 'system/system_create.html')

# システム一覧画面
def system_list(request):
    return render(request, 'system/system_list.html')

# 該当システム詳細画面
def system_details(request):
    return render(request, 'system/system_details.html')


# アカウントダッシュボード（生徒/教員どちらでも動作する簡易版）
def account_view(request):
    """ログインユーザーに紐づく Account を可能な限り探して適切なテンプレートを表示します。

    完全なアプリ設計では Django の User と Account を関連付ける方が望ましいですが、
    ここでは利用可能な情報で柔軟にフォールバックします。
    """
    try:
        acc = get_logged_account(request)
        if acc:
            if acc.account_type == 'teacher':
                return render(request, 'accounts/t_account.html', {'account': acc})
            return render(request, 'accounts/s_account.html', {'account': acc})
    except Exception:
        pass

    # フォールバック: 生徒アカウント画面を表示
    return render(request, 'accounts/s_account.html')


def s_account_view(request):
    """生徒アカウント専用ビュー（テンプレートが存在するため簡易に実装）"""
    return render(request, 'accounts/s_account.html')


def group_create(request):
    """グループ作成画面レンダリング（POST 処理は未実装）"""
    if request.method == 'POST':
        # TODO: 実際の作成処理を実装
        return redirect('group_menu')
    return render(request, 'group/create_group.html')


def add_member_popup(request):
    """グループにメンバーを追加するポップアップ（簡易レンダリング）"""
    return render(request, 'group/add_group.html')


def group_menu(request):
    """グループメニュー画面を表示"""
    return render(request, 'group/group_menu.html')


def group_join_confirm(request):
    """グループ参加確認画面

    GET: 確認画面を表示。クエリパラメータ `group_name` を受け取れる。
    POST: フォームで `action` が 'join' なら参加処理（プレースホルダ）を行い、
          それ以外はキャンセル扱いで `group_menu` に戻す。
    """
    # この画面ではグループ名は表示せず、する/しない を選ぶだけにする
    # GET パラメータは無視してテンプレートを表示する
    # アカウント種別によって遷移先を分岐する
    acc = get_logged_account(request)
    if acc is not None and acc.account_type == 'teacher':
        # 教員は確認不要なので仮ホームに遷移（テンプレートをレンダリング）
        return render(request, 'accounts/karihome.html')

    # 生徒または未ログインは確認画面を表示／POST は次の画面へ
    if request.method == 'POST':
        action = request.POST.get('action')
        # ここでは選択後にグループメニューへ遷移させる（必要なら変更）
        return redirect('group_menu')
    # GET: 確認画面を表示
    return render(request, 'group/join_confirm.html')


# 開発用: パスワード再設定確認テンプレートをトークンなしでプレビューする簡易ビュー
def preview_password_reset_confirm(request):
    """開発環境でテンプレート確認のために、SetPasswordForm の空フォームを渡してレンダリングするビュー。

    本番にデプロイする際はこの URL を削除してください。
    """
    form = SetPasswordForm(user=None)
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


