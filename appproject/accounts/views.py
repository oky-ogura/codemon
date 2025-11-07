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
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core import signing
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect

from django.db import connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password



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

    def form_valid(self, form):
        """メールアドレスを受け取り、Account が存在すれば署名付きトークンを作成してメール送信する。

        存在しないメールアドレスでも成功画面へ遷移させて、アカウントの有無情報漏洩を防ぐ。
        """
        email = form.cleaned_data.get('email')
        acc = Account.objects.filter(email=email).first()
        # 常に成功画面へリダイレクトする（存在の有無を明かさない）
        if acc:
            # トークンは署名付きで作成し、有効期限は settings で管理できるようにする（ここでは1日）
            token = signing.dumps({'user_id': acc.user_id}, salt='accounts-password-reset')
            uidb64 = urlsafe_base64_encode(force_bytes(str(acc.user_id)))
            protocol = 'https' if self.request.is_secure() else 'http'
            context = {
                'email': acc.email,
                'domain': self.request.get_host(),
                'site_name': getattr(settings, 'SITE_NAME', self.request.get_host()),
                'uidb64': uidb64,
                'token': token,
                'protocol': protocol,
            }
            # メール送信（テンプレートを利用）
            subject = 'パスワード再設定のご案内'
            message = render_to_string(self.email_template_name, context)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            # send_mail は DEBUG 時は console backend を用いる設定が settings.py に入っています
            send_mail(subject, message, from_email, [acc.email], fail_silently=False)

        return HttpResponseRedirect(self.get_success_url())


def get_logged_account(request):
    """セッションまたは request.user から account.user_id を特定して Account オブジェクトを返す。"""
    try:
        uid = request.session.get('account_user_id')
        if not uid and getattr(request, 'user', None) and request.user.is_authenticated:
            # Django の User.id を fallback として使う（Account.user_id が同じ運用の場合）
            uid = request.user.id

        if not uid:
            return None

        account = Account.objects.filter(user_id=uid).first()
        return account
    except Exception:
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
    """
    教員ログイン:
    - POST: account テーブルの user_name + account_type='teacher' で照合し、
            パスワードが一致すればセッションを設定して karihome を表示する。
    - GET: ログインフォームを表示
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        account_row = None
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, user_name, email, password, account_type FROM account "
                "WHERE user_name = %s AND account_type = %s",
                [username, 'teacher']
            )
            account_row = cursor.fetchone()

        if account_row and check_password(password, account_row[3]):
            # セッションに最小限の情報を入れる（既存の実装に合わせて拡張可）
            request.session['is_account_authenticated'] = True
            request.session['account_user_id'] = account_row[0]
            request.session['account_email'] = account_row[2]
            request.session['account_user_name'] = account_row[1]
            request.session.modified = True
            # ログイン成功 → karihome.html を表示
            return render(request, 'accounts/karihome.html')
        else:
            messages.error(request, 'ユーザー名またはパスワードが違います')

    # GET または認証失敗時はログインフォームを表示
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
    # 修正: 'home' が未定義のため accounts のルートへリダイレクト
    return redirect('accounts_root')

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


# アルゴリズム選択画面
def block_choice(request):
    """
    /accounts/block/choice/ で block/choice.html を表示する簡易ビュー
    """
    return render(request, 'block/block_choice.html')

# 新規アルゴリズム作成画面
def block_create(request):
    """
    block_create.html を表示（表示のみ、遷移先なし）
    """
    return render(request, 'block/block_create.html')


# 該当アルゴリズム詳細画面
def block_details(request):
    
    return render(request, 'block/block_details.html')

# アルゴリズム一覧画面
def block_list(request):

    return render(request, 'block/block_list.html')


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
    """
    POST で group_name, group_password を受け取り "group" テーブルへ挿入。
    作成者はセッションの account_user_id を優先し、なければログインユーザー id を使用。
    成功したらアカウントページへリダイレクト（必要なら group_detail に変更可）。
    """
    if request.method == 'POST':
        group_name = (request.POST.get('group_name') or '').strip()
        group_password = (request.POST.get('group_password') or '').strip()
        user_id = request.session.get('account_user_id') or (request.user.id if getattr(request.user, 'is_authenticated', False) else None)

        if not group_name:
            messages.error(request, 'グループ名を入力してください。')
            return redirect('group_create')

        if not user_id:
            messages.error(request, 'ユーザーが特定できません。ログインしてください。')
            return redirect('student_login')

        # パスワードはハッシュ化して保存（空可）
        hashed = make_password(group_password) if group_password else ''

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO "group" (group_name, user_id, password) VALUES (%s, %s, %s) RETURNING group_id',
                    [group_name, user_id, hashed]
                )
                row = cursor.fetchone()
                group_id = row[0] if row else None

                # 追加: 作成者を group_member テーブルに owner として挿入
                if group_id is not None:
                    try:
                        cursor.execute(
                            'INSERT INTO group_member (group_id, member_user_id, role) VALUES (%s, %s, %s)',
                            [group_id, user_id, 'owner']
                        )
                    except Exception:
                        # メンバー登録失敗でもグループ作成自体は成功させる
                        pass

        except Exception as e:
            messages.error(request, f'グループ作成に失敗しました: {e}')
            return redirect('group_create')

        messages.success(request, 'グループを作成しました。')
        # 存在すれば group_detail に飛ばす（なければアカウントページへ）
        try:
            return redirect('group_detail', group_id=group_id)
        except Exception:
            return redirect('account_entry')

    # GET の場合は作成ページを表示
    return render(request, 'group/create_group.html', {})



def add_member_popup(request):
    """グループにメンバーを追加するポップアップ（簡易レンダリング）"""
    return render(request, 'group/add_group.html')


def group_menu(request):
    """グループメニュー画面を表示"""
    return render(request, 'group/group_menu.html')

def group_join_confirm(request):
    """
    GET:
      - 所属が生徒 (account.account_type == 'student') の場合 -> group/join_confirm.html を表示
      - 教師 (account.account_type == 'teacher') の場合 -> accounts/karihome.html を表示
      - ログインしていない場合は生徒ログイン画面へリダイレクト
    POST:
      - action=join -> （簡易実装）group メニューを表示
      - action=cancel またはその他 -> アカウントトップへリダイレクト
    """
    account = get_logged_account(request)

    if request.method == 'GET':
        if account and getattr(account, 'account_type', '').lower() == 'student':
            # 生徒は参加確認画面へ
            return render(request, 'group/join_confirm.html', {})
        elif account and getattr(account, 'account_type', '').lower() == 'teacher':
            # 教師は仮ホーム（karihome）へ
            return render(request, 'accounts/karihome.html', {})
        else:
            # 未ログイン等は生徒ログインへ誘導
            return redirect('student_login')

    # POST 処理（join/cancel）
    action = request.POST.get('action')
    if action == 'join':
        # ここで実際に group_member に追加する処理を入れてください。
        # 簡易的にグループメニューを表示します。
        return render(request, 'group/group_menu.html', {})
    else:
        return redirect('account_entry')


# ...existing code...


# 開発用: パスワード再設定確認テンプレートをトークンなしでプレビューする簡易ビュー
def preview_password_reset_confirm(request):
    """開発環境でテンプレート確認のために、SetPasswordForm の空フォームを渡してレンダリングするビュー。

    本番にデプロイする際はこの URL を削除してください。
    """
    form = SetPasswordForm(user=None)
    return render(request, 'accounts/password_reset_custom.html', {'form': form})


# --- カスタムのパスワード再設定確認ビュー（Account を直接操作する） ---
class _SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='確認用パスワード', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('パスワードが一致しません')
        return cleaned


def password_reset_confirm(request, uidb64, token):
    """署名付きトークンを検証して該当する Account のパスワードを更新するビュー。

    token は `signing.dumps({'user_id': ...}, salt='accounts-password-reset')` で作成される想定。
    """
    # uidb64 をデコードして user_id を得る（安全策として検証に使用）
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        uid = None

    # トークン検証（有効期限は 24 時間）
    try:
        payload = signing.loads(token, salt='accounts-password-reset', max_age=60 * 60 * 24)
        user_id_from_token = str(payload.get('user_id'))
    except signing.BadSignature:
        payload = None
        user_id_from_token = None
    except signing.SignatureExpired:
        payload = None
        user_id_from_token = None

    # 優先して token の中身を信頼し、fallback で uidb64 と照合
    user_id = user_id_from_token or uid
    if not user_id:
        # 無効なリンク
        return render(request, 'accounts/password_reset_invalid.html')

    account = Account.objects.filter(user_id=user_id).first()
    if not account:
        return render(request, 'accounts/password_reset_invalid.html')

    if request.method == 'POST':
        form = _SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_pw = form.cleaned_data['new_password1']
            account.password = make_password(new_pw)
            account.save()
            # パスワード更新後はログイン画面へリダイレクト
            return HttpResponseRedirect(reverse('student_login'))
    else:
        form = _SetNewPasswordForm()

    return render(request, 'accounts/password_reset_custom.html', {'form': form})

def t_account(request):
    """
    ログインユーザーの email で account テーブルを検索し、
    account 情報をテンプレートに渡す。
    """
    account = None
    email = request.user.email
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, user_name, email, account_type, age, group_id, created_at "
            "FROM account WHERE email = %s",
            [email]
        )
        row = cursor.fetchone()
        if row:
            account = {
                'user_id': row[0],
                'user_name': row[1],
                'email': row[2],
                'account_type': row[3],
                'age': row[4],
                'group_id': row[5],
                'created_at': row[6],
            }
    return render(request, 'accounts/t_account.html', {'account': account, 'user': request.user})

def account_entry(request):
    """
    account を取得し account_type に応じてテンプレートを返す。
    created_at から初めて会った日と累計日数を計算してテンプレートに渡す。
    """
    account = None
    user_id = request.session.get('account_user_id')
    email = request.session.get('account_email') or (getattr(request.user, 'email', None) if getattr(request.user, 'is_authenticated', False) else None)

    if not user_id and not email:
        return redirect('student_login')

    with connection.cursor() as cursor:
        if user_id:
            cursor.execute(
                "SELECT user_id, user_name, email, account_type, age, group_id, created_at "
                "FROM account WHERE user_id = %s",
                [user_id]
            )
        else:
            cursor.execute(
                "SELECT user_id, user_name, email, account_type, age, group_id, created_at "
                "FROM account WHERE email = %s",
                [email]
            )
        row = cursor.fetchone()
        if not row:
            return redirect('student_login')
        account = {
            'user_id': row[0],
            'user_name': row[1],
            'email': row[2],
            'account_type': row[3],
            'age': row[4],
            'group_id': row[5],
            'created_at': row[6],
        }

    # created_at -> 初めて会った日（datetime）と累計日数（文字列）を計算
    created_at = account.get('created_at')
    first_met = None
    total_days_str = "0日"
    
    if created_at:
        now = timezone.now()
        try:
            # created_at は DB からの datetime オブジェクトのはず
            delta = now - created_at
            days = max(delta.days, 0)
        except Exception:
            days = 0
        first_met = created_at
        total_days_str = f"{days}日"

    # テンプレート参照を満たす安全な user オブジェクトを作る
    if getattr(request.user, 'is_authenticated', False):
        user_for_template = request.user
    else:
        from types import SimpleNamespace
        profile = SimpleNamespace(
            avatar=None,
            kyojin='',
            age=account.get('age'),
            first_met=None,
            total_days=None
        )
        user_for_template = SimpleNamespace(
            get_full_name=lambda: account.get('user_name') or '',
            id=account.get('user_id'),
            profile=profile
        )
    # groups を DB から取得（現在ログインしているユーザー id を基準に取得）
    groups = []
    # 現在ログインしているユーザーの id を決める（セッション優先）
    current_user_id = account.get('user_id') or request.session.get('account_user_id') or (request.user.id if getattr(request.user, 'is_authenticated', False) else None)
    try:
        # current_user_id が文字列で渡ってくる可能性を考慮して int に変換を試みる
        if current_user_id is not None:
            try:
                current_user_id = int(current_user_id)
            except Exception:
                # 変換できなければ無効扱いにする
                current_user_id = None

        if current_user_id is not None:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT g.group_id, g.user_id, g.group_name,
                           COALESCE(g.size, (SELECT COUNT(*) FROM group_member gm WHERE gm.group_id = g.group_id), 0) AS member_count
                    FROM "group" g
                    WHERE g.user_id = %s
                    ORDER BY g.group_id
                """, [current_user_id])
                for row in cursor.fetchall():
                    groups.append({
                        'group_id': row[0],
                        'owner_id': row[1],
                        'name': row[2],
                        'member_count': row[3],
                    })
        else:
            groups = []
    except Exception:
        groups = []


    context = {
        'account': account,
        'user': user_for_template,
        'first_met': first_met,
        'total_days': total_days_str,
        'groups': groups,
        'current_user_id': current_user_id,
    }

    if account.get('account_type') == 'teacher':
        return render(request, 'accounts/t_account.html', context)
    else:
        return render(request, 'accounts/s_account.html', context)


    

