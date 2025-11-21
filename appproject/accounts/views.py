from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
 # password ハッシュ化はフォーム側で行うように変更しました
from .forms import TeacherSignupForm, StudentSignupForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from .models import Account, Group, GroupMember
from django.conf import settings
from django import forms
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core import signing
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponseForbidden, FileResponse, JsonResponse

from django.db import connection, transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
import logging
from django.utils.dateparse import parse_datetime, parse_date
import datetime
try:
    from codemon.views import _get_write_owner
except Exception:
    # If import fails (circular import in some contexts), define a fallback that mimics codemon._get_write_owner
    def _get_write_owner(request):
        # Prefer session-based Account, fall back to request.user if authenticated, else None
        try:
            uid = request.session.get('account_user_id')
            if uid:
                return Account.objects.filter(user_id=uid).first()
        except Exception:
            pass
        if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
            return request.user
        return None


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
            back = reverse('accounts:teacher_login')
        else:
            back = reverse('accounts:student_login')
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
            # サインアップ直後にセッションへアカウント情報を入れておくと
            # 以降のフロー（AI設定など）でアカウントが参照しやすくなる
            try:
                request.session['is_account_authenticated'] = True
                request.session['account_user_id'] = instance.user_id
                request.session['account_email'] = instance.email
                request.session['account_user_name'] = instance.user_name
                request.session.modified = True
                try:
                    request.session.save()
                except Exception:
                    pass
            except Exception:
                pass
            # 登録後は AI 外見設定へ遷移
            return redirect('accounts:ai_appearance')
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
            # session にアカウント情報をセットしておく（サインアップ直後の扱いを容易にする）
            try:
                request.session['is_account_authenticated'] = True
                request.session['account_user_id'] = instance.user_id
                request.session['account_email'] = instance.email
                request.session['account_user_name'] = instance.user_name
                request.session.modified = True
                try:
                    request.session.save()
                except Exception:
                    pass
            except Exception:
                pass
            # サインアップ後は AI 外見設定へ遷移
            return redirect('accounts:ai_appearance')
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
            try:
                request.session.save()
            except Exception:
                pass
            # --- Django標準ユーザーとのブリッジ（teacher 版） ---
            try:
                User = get_user_model()
                django_user, created = User.objects.get_or_create(username=account_row[2], defaults={'email': account_row[2]})
                if created or not django_user.password:
                    django_user.set_password(password)
                    django_user.save()
                login(request, django_user)
            except Exception as e:
                print(f"DEBUG teacher_login bridge error: {e}")
            # セッションID生成（存在しない場合）
            if not request.session.session_key:
                request.session.cycle_key()
            print(f"DEBUG teacher_login: session_key={request.session.session_key} data={dict(request.session)}")
            # 古いエラーメッセージをクリア
            try:
                list(get_messages(request))
            except Exception:
                pass
            # リダイレクトで Set-Cookie を確実に反映
            return redirect('accounts:karihome')
        else:
            # 認証失敗の原因が "別の種別のアカウントで存在している" 可能性があるため確認する
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT user_id, user_name, email, password, account_type FROM account WHERE user_name = %s OR email = %s LIMIT 1",
                        [username, username]
                    )
                    alt_row = cursor.fetchone()
                if alt_row and check_password(password, alt_row[3]):
                    acct_type = (alt_row[4] or '').lower() if len(alt_row) > 4 else ''
                    if acct_type != 'teacher':
                        messages.error(request, 'このアカウントはここではログインできません')
                    else:
                        messages.error(request, 'ユーザー名またはパスワードが違います')
                else:
                    messages.error(request, 'ユーザー名またはパスワードが違います')
            except Exception:
                messages.error(request, 'ユーザー名またはパスワードが違います')

    # GET または認証失敗時はログインフォームを表示
    return render(request, 'accounts/t_login.html')

def login_choice(request):
    """ログイン種別選択（暫定）。未実装のため生徒ログインへフォールバック。"""
    return redirect('accounts:student_login')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Account テーブルを使って認証（auth_user を利用しない）
        acc = Account.objects.filter(email=username).first() or Account.objects.filter(user_name=username).first()
        if acc and check_password(password, acc.password):
            # このログイン画面は生徒用。アカウント種別が student でない場合はログイン不可とする
            try:
                acct_type = getattr(acc, 'account_type', '') or ''
            except Exception:
                acct_type = ''
            if acct_type.lower() != 'student':
                messages.error(request, 'このアカウントはここではログインできません')
                return render(request, 'accounts/s_login.html')

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
            # --- Django標準ユーザーとのブリッジ（login_required などの互換性確保） ---
            try:
                User = get_user_model()
                # email を username に使う（既存ユーザーがあれば再利用）
                django_user, created = User.objects.get_or_create(username=acc.email, defaults={'email': acc.email})
                # パスワード未設定なら設定（ハッシュ済みを避けるため set_password 使用）
                if created or not django_user.password:
                    django_user.set_password(password)
                    django_user.save()
                # 認証後 login() で request.user を有効化
                login(request, django_user)
            except Exception as e:
                print(f"DEBUG student_login bridge error: {e}")
            # セッションID生成（存在しない場合）
            if not request.session.session_key:
                request.session.cycle_key()
            # デバッグ: セッション情報を出力
            print(f"DEBUG student_login: session_key = {request.session.session_key}")
            print(f"DEBUG student_login: session data = {dict(request.session)}")
            # 古いエラーメッセージをクリア
            try:
                list(get_messages(request))
            except Exception:
                pass
            # リダイレクトにより Set-Cookie を確実に反映
            return redirect('accounts:karihome')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'accounts/s_login.html')

def karihome(request):
    """簡易ビュー: accounts/karihome.html を表示する。テンプレートは既にあるため GET で表示するだけ。"""
    return render(request, 'accounts/karihome.html')

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
    # ログアウト後はログイン選択ページへ遷移させる（teacher / student を選ぶ画面）
    try:
        return redirect('accounts:login_choice')
    except Exception:
        return redirect('/')

# --- セッションベース認証簡易デコレータ & karihome ビュー追加 ---
from functools import wraps

def account_session_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('is_account_authenticated'):
            login_url = reverse('accounts:student_login')
            next_url = request.get_full_path()
            return redirect(f"{login_url}?next={next_url}")
        return view_func(request, *args, **kwargs)
    return _wrapped

@account_session_required
def karihome(request):
    return render(request, 'accounts/karihome.html')

def login_choice(request):
    """ログイン種別の選択ページ（教師 or 生徒）を表示する簡易ビュー"""
    # 単純な選択ページを表示するだけ。テンプレート内でそれぞれのログインページへ遷移する。
    return render(request, 'accounts/login_choice.html')

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
        return redirect('accounts:ai_initial')

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
        return redirect('accounts:ai_initial')

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
    from .models import Account  # ← 忘れずに追加

    if request.method != 'POST':
        return redirect('accounts:ai_initial')

    ai_name = request.POST.get('ai_name', '')
    ai_personality = request.POST.get('ai_personality', '')
    ai_speech = request.POST.get('ai_speech', '')
    appearance = request.POST.get('appearance', '')

    acc = None
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

    # ログイン済みアカウントが取得できなかった場合
    if acc is None:
        try:
            email = request.session.get('pending_account_email') or request.session.get('account_email')
            name = request.session.get('pending_account_name') or request.session.get('account_user_name')
            if email:
                acc = Account.objects.filter(email=email).first()
            if acc is None and name:
                acc = Account.objects.filter(user_name=name).first()
        except Exception:
            acc = None

    # ✅ リダイレクトに変更
    try:
        if acc and getattr(acc, 'account_type', '').lower() == 'student':
            # 生徒 → group_join_confirm へ遷移
            return redirect('accounts:group_join_confirm')
        elif acc and getattr(acc, 'account_type', '').lower() == 'teacher':
            # 教員 → karihome を表示
            return render(request, 'accounts/karihome.html')
    except Exception:
        pass

    # フォールバック
    return redirect('accounts:accounts_root')

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


def login_choice(request):
    """ログイン種別選択画面（教員 / 生徒）を表示するビュー"""
    return render(request, 'accounts/login_choice.html')

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
            try:
                return account_entry(request)
            except Exception:
                # Fallback to rendering minimal templates if delegation fails
                if acc.account_type == 'teacher':
                    return render(request, 'accounts/t_account.html', {'account': acc})
                return render(request, 'accounts/s_account.html', {'account': acc})
    except Exception:
        pass

    # フォールバック: 生徒アカウント画面を表示
    return render(request, 'accounts/s_account.html')


def s_account_view(request):
    """生徒アカウント専用ビュー（テンプレートが存在するため簡易に実装）"""
    account = None
    user_id = request.session.get('account_user_id')
    email = request.session.get('account_email') or (getattr(request.user, 'email', None) if getattr(request.user, 'is_authenticated', False) else None)

    try:
        with connection.cursor() as cursor:
            if user_id:
                cursor.execute(
                    "SELECT user_id, user_name, email, account_type, age, group_id, created_at "
                    "FROM account WHERE user_id = %s",
                    [user_id]
                )
            elif email:
                cursor.execute(
                    "SELECT user_id, user_name, email, account_type, age, group_id, created_at "
                    "FROM account WHERE email = %s",
                    [email]
                )
            else:
                cursor = None

            if cursor:
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
    except Exception:
        account = None

    # Prepare fallback display values
    first_met = None
    total_days_str = '0日'
    if account and account.get('created_at'):
        created_at_val = account.get('created_at')
        try:
            if isinstance(created_at_val, str):
                dt = parse_datetime(created_at_val)
                if dt is None:
                    d = parse_date(created_at_val)
                    if d:
                        dt = datetime.datetime.combine(d, datetime.time.min)
                created_at_val = dt

            if created_at_val is not None and isinstance(created_at_val, datetime.datetime):
                # make timezone-aware if needed
                if timezone.is_naive(created_at_val):
                    try:
                        created_at_val = timezone.make_aware(created_at_val, timezone.get_current_timezone())
                    except Exception:
                        # fallback: assume naive is in UTC
                        created_at_val = timezone.make_aware(created_at_val, datetime.timezone.utc)

                now = timezone.now()
                delta = now - created_at_val
                days = max(getattr(delta, 'days', 0), 0)
                first_met = created_at_val
                total_days_str = f"{days}日"
                # 人間可読の経過時間文字列
                try:
                    time_since_created = format_timedelta(delta)
                except Exception:
                    time_since_created = ''
            else:
                # could not parse datetime, keep fallback
                first_met = account.get('created_at')
                total_days_str = '0日'
                time_since_created = ''
        except Exception:
            first_met = account.get('created_at')
            total_days_str = '0日'
            time_since_created = ''

    # Get joined group info if available
    joined_group = None
    
    try:
        gid = account.get('group_id') if account else None
        if gid:
            with connection.cursor() as cursor:
                cursor.execute('SELECT group_id, group_name, user_id FROM "group" WHERE group_id = %s', [gid])
                g = cursor.fetchone()
                if g:
                    creator_name = ''
                    try:
                        with connection.cursor() as c2:
                            c2.execute('SELECT user_name FROM account WHERE user_id = %s', [g[2]])
                            r = c2.fetchone()
                            if r:
                                creator_name = r[0]
                    except Exception:
                        creator_name = ''
                    # Try to build a URL to codemon:group_detail if that URL name exists
                    detail_url = None
                    try:
                        detail_url = reverse('codemon:group_detail', args=[g[0]])
                    except Exception:
                        detail_url = None
                    joined_group = {'group_id': g[0], 'group_name': g[1], 'creator_name': creator_name, 'detail_url': detail_url}
    except Exception:
        joined_group = None

    created_at_raw = account.get('created_at') if account else None
    created_at_type = type(created_at_raw).__name__ if created_at_raw is not None else None
    # Render template with gathered context (fall back to template defaults if account missing)
    return render(request, 'accounts/karihome.html', {
        'account': account,
        'first_met': first_met,
        'total_days': total_days_str,
        'joined_group': joined_group,
        'created_at_raw': created_at_raw,
        'created_at_type': created_at_type,
        'time_since_created': time_since_created,
    })


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
            return redirect('accounts:group_create')

        if not user_id:
            messages.error(request, 'ユーザーが特定できません。ログインしてください。')
            return redirect('accounts:student_login')
        # パスワードはハッシュ化して保存（空可）
        hashed = make_password(group_password) if group_password else ''

        try:
            # まず Account インスタンスを解決
            account_owner = Account.objects.filter(user_id=user_id).first()

            # トランザクション内でグループ作成とメンバー登録を行い、途中で失敗したらロールバックする
            with transaction.atomic():
                # 多くの既存 DB スキーマでは group.password が NOT NULL の場合があるため
                # raw SQL で確実に挿入する
                with connection.cursor() as cursor:
                    cursor.execute('INSERT INTO "group" (group_name, user_id, password, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, now(), now())', [group_name, user_id, hashed or '', True])
                    # 挿入した行を取得（group_name と user_id の組で最新のものを選ぶ）
                    cursor.execute('SELECT group_id FROM "group" WHERE group_name = %s AND user_id = %s ORDER BY group_id DESC LIMIT 1', [group_name, user_id])
                    row = cursor.fetchone()
                    group_id = row[0] if row else None

                if group_id is None:
                    raise Exception('グループ作成後に group_id を取得できませんでした')

                # ORM オブジェクトとして利用可能なら取得しておく（proxy を使っているため models の互換性に注意）
                group = Group.objects.filter(group_id=group_id).first()

                # DB スキーマに member_id が存在して NOT NULL 制約がある環境があるため
                # 安全策として raw SQL で member_user_id と member_id の両方を明示して挿入する。
                with connection.cursor() as cursor:
                    # 重複防止: 既に同じ member_user_id が登録されていないか確認
                    cursor.execute('SELECT 1 FROM group_member WHERE group_id = %s AND member_user_id = %s', [group_id, user_id])
                    if not cursor.fetchone():
                        try:
                            cursor.execute('INSERT INTO group_member (group_id, member_user_id, member_id, role, created_at) VALUES (%s, %s, %s, %s, now())', [group_id, user_id, user_id, 'teacher'])
                        except Exception:
                            # まれにカラム名/制約が違うスキーマが混在する可能性があるのでフォールバックで別カラム順を試す
                            try:
                                cursor.execute('INSERT INTO group_member (group_id, member_user_id, role, created_at) VALUES (%s, %s, %s, now())', [group_id, user_id, 'teacher'])
                            except Exception:
                                # ここまで失敗したら例外を再送出して transaction.atomic に任せる
                                raise

        except Exception as e:
            # ログに完全なトレースを残す（開発用）
            logging.exception('group_create failed')
            # ユーザ向けのメッセージを表示して作成ページへ戻す
            messages.error(request, f'グループ作成に失敗しました: {e}')
            return redirect('accounts:group_create')

        except Exception as e:
            messages.error(request, f'グループ作成に失敗しました: {e}')
            return redirect('accounts:group_create')

        messages.success(request, 'グループを作成しました。')
        # 要求: 作成後は教員アカウント用テンプレート `t_account.html` に戻す
        # URLconf では t_account ページは name='account_dashboard' にマッピングされているため
        # ここではその名前へリダイレクトする
        try:
            return redirect('accounts:account_dashboard')
        except Exception:
            # 万一リダイレクトに失敗したらアカウントトップへフォールバック
            return redirect('accounts:account_entry')

    # GET の場合は作成ページを表示
    return render(request, 'group/create_group.html', {})



def add_member_popup(request):
    """グループにメンバーを追加するポップアップ（簡易レンダリング）"""
    return render(request, 'group/add_group.html')


def group_menu(request, group_id):
    """グループメニュー画面を表示（group_id 必須）"""
    # 最低限のコンテキストをテンプレートへ渡す（必要なら詳細情報を増やす）
    try:
        group = get_object_or_404(Group, group_id=group_id, is_active=True)
        # group_member テーブルに is_active カラムがない環境もあるため、存在に依らず単純に取得する
        members_qs = GroupMember.objects.filter(group=group).select_related('member')
        member_count = members_qs.count()
        members = list(members_qs)
    except Exception:
        group = None
        members = []
        member_count = 0

    return render(request, 'group/group_menu.html', {
        'group': group,
        'members': members,
        'member_count': member_count,
        'group_id': group_id,
    })


def group_menu_redirect(request):
    """互換性のためのフォールバック: 旧パス /groups/menu/ へのアクセスをアカウント画面へリダイレクトする。"""
    # 既存のコードベースでは account_entry がアカウントトップを返すため、そこへ誘導する
    try:
        return redirect('accounts:account_entry')
    except Exception:
        return redirect('/')


def group_delete_confirm(request, group_id):
    """グループ削除の確認画面を表示する（GET）。削除確定は POST で accounts:group_delete (codemon.views.group_delete) を呼ぶ。"""
    owner = _get_write_owner(request)
    if owner is None:
        return redirect('accounts:student_login')

    try:
        group = Group.objects.get(group_id=group_id, is_active=True)
    except Group.DoesNotExist:
        messages.error(request, '指定されたグループが見つかりません')
        return redirect('accounts:account_entry')

    # 所有者以外は削除できない
    if getattr(owner, 'type', '') != 'teacher' or getattr(group, 'owner_id', None) != getattr(owner, 'user_id', None):
        messages.error(request, 'グループの削除権限がありません')
        return redirect('accounts:account_entry')

    # メンバー数を数える（GroupMember テーブルを利用）
    try:
        member_count = GroupMember.objects.filter(group=group).count()
    except Exception:
        member_count = 0

    return render(request, 'group/group_delete_confirm.html', {
        'group': group,
        'member_count': member_count,
    })

def group_delete(request, group_id):
    """POSTで受け取り、指定グループのメンバーとアカウントの紐付けを削除し、グループ本体を削除します。"""
    if request.method != 'POST':
        # 確認ページへ誘導（POST以外は削除を行わない）
        return redirect('accounts:group_delete_confirm', group_id=group_id)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # group_member テーブルから該当 group_id のメンバーを削除
                cursor.execute('DELETE FROM group_member WHERE group_id = %s', [group_id])
                # account テーブルの group_id を NULL にして紐付け解除
                cursor.execute('UPDATE account SET group_id = NULL WHERE group_id = %s', [group_id])
                # 最後に group 本体を削除（テーブル名が予約語のためダブルクォートで囲む）
                cursor.execute('DELETE FROM "group" WHERE group_id = %s', [group_id])
        messages.success(request, 'グループを削除しました。')
    except Exception as e:
        messages.error(request, f'グループの削除に失敗しました: {e}')
    return redirect('accounts:account_entry')


def group_menu_redirect(request):
    """グループメニュー root への互換ハンドラ。

    セッションやログインユーザーから所属する（または所有する）最初のグループを探し、
    見つかればその `group_menu` へリダイレクトする。見つからなければグループ一覧/作成へ誘導する。
    """
    # 優先順: セッションの current group -> 自分が所有するグループの最初 -> アカウントページ
    try:
        gid = request.session.get('current_group_id')
        if gid:
            return redirect('accounts:group_menu', group_id=gid)

        # 試しに現在のユーザー id を取得して所有グループを検索
        current_user_id = request.session.get('account_user_id') or (request.user.id if getattr(request.user, 'is_authenticated', False) else None)
        if current_user_id:
            with connection.cursor() as cursor:
                cursor.execute('SELECT group_id FROM "group" WHERE user_id = %s ORDER BY group_id LIMIT 1', [current_user_id])
                row = cursor.fetchone()
                if row:
                    return redirect('accounts:group_menu', group_id=row[0])
    except Exception:
        pass

    # フォールバック: グループ作成ページへ誘導
    return redirect('accounts:group_create')


def group_detail(request, group_id):
    """Proxy to show group detail using `codemon.views.group_detail` if available,
    otherwise render a simple accounts template.
    """
    try:
        from codemon import views as codemon_views
        # Prefer codemon's implementation when present
        if hasattr(codemon_views, 'group_detail'):
            return codemon_views.group_detail(request, group_id)
    except Exception:
        pass

    # Fallback: try to query minimal group info and render accounts template
    group = None
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT group_id, group_name, user_id FROM "group" WHERE group_id = %s', [group_id])
            row = cursor.fetchone()
            if row:
                group = {'group_id': row[0], 'group_name': row[1], 'owner_id': row[2]}
    except Exception:
        group = None

    if group is None:
        messages.error(request, '指定されたグループが見つかりません')
        return redirect('accounts:account_entry')

    return render(request, 'group/group_check.html', {'group': group})


def group_delete_confirm(request, group_id):
    """表示用の削除確認ページ。POST 実行は `codemon.views.group_delete` を使う想定。"""
    group = None
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT group_id, group_name, user_id FROM "group" WHERE group_id = %s', [group_id])
            row = cursor.fetchone()
            if row:
                group = {'group_id': row[0], 'group_name': row[1], 'owner_id': row[2]}
    except Exception:
        group = None

    if group is None:
        messages.error(request, '指定されたグループが見つかりません')
        return redirect('accounts:account_entry')

    return render(request, 'group/group_delete_confirm.html', {'group': group})


def group_remove_member(request, group_id, member_id):
    """グループからメンバーを削除するラッパー。

    可能なら `codemon.views.group_remove_member` を呼び出し、なければ簡易に
    `group_member` テーブルの `is_active` を False にして論理削除します。
    """
    try:
        from codemon import views as codemon_views
        if hasattr(codemon_views, 'group_remove_member'):
            return codemon_views.group_remove_member(request, group_id, member_id)
    except Exception:
        pass

    # フォールバック実装: セッションの権限チェックは簡易にしておく
    try:
        current_user_id = request.session.get('account_user_id') or (request.user.id if getattr(request.user, 'is_authenticated', False) else None)
        # 簡易権限制御: current_user_id がグループの owner であるか、または自身を削除する場合のみ許可
        with connection.cursor() as cursor:
            cursor.execute('SELECT user_id FROM "group" WHERE group_id = %s', [group_id])
            row = cursor.fetchone()
            owner_id = row[0] if row else None

            if current_user_id is None:
                messages.error(request, 'ログインが必要です')
                return redirect('accounts:student_login')

            if int(current_user_id) != int(owner_id) and int(current_user_id) != int(member_id):
                return HttpResponseForbidden('この操作を行う権限がありません')

            # 論理削除フラグがある場合は更新、なければ削除
            try:
                cursor.execute('UPDATE group_member SET is_active = FALSE WHERE group_id = %s AND member_user_id = %s', [group_id, member_id])
            except Exception:
                # fallback: attempt delete
                try:
                    cursor.execute('DELETE FROM group_member WHERE group_id = %s AND member_user_id = %s', [group_id, member_id])
                except Exception as e:
                    messages.error(request, f'メンバー削除に失敗しました: {e}')
                    return redirect('accounts:group_detail', group_id=group_id)

        messages.success(request, 'メンバーをグループから削除しました')
        return redirect('accounts:group_detail', group_id=group_id)
    except Exception as e:
        messages.error(request, f'メンバー削除に失敗しました: {e}')
        return redirect('accounts:group_detail', group_id=group_id)


def group_invite(request, group_id):
    """グループへメンバーを追加する処理（POST）またはフォーム表示（GET）を行う簡易ビュー。

    - POST: `member_email` または `member_user_id` を受け取り `group_member` テーブルへ挿入する。
    - GET: メンバー追加フォームへリダイレクトする。
    """
    if request.method != 'POST':
        return redirect('accounts:group_add_member_form', group_id=group_id)

    member_input = (request.POST.get('member_email') or request.POST.get('member_user_id') or '').strip()
    role = request.POST.get('role', 'member')

    if not member_input:
        messages.error(request, '追加するメンバーの情報を指定してください。')
        return redirect('accounts:group_add_member_form', group_id=group_id)

    member_user_id = None
    try:
        # まず数値として解釈を試みる
        try:
            member_user_id = int(member_input)
        except Exception:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM account WHERE email = %s OR user_name = %s", [member_input, member_input])
                row = cursor.fetchone()
                if row:
                    member_user_id = row[0]

        if not member_user_id:
            messages.error(request, 'そのユーザーは見つかりませんでした。')
            return redirect('accounts:group_add_member_form', group_id=group_id)

        # 挿入（既存の重複チェックは簡易に任せる）
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO group_member (group_id, member_user_id, role) VALUES (%s, %s, %s)',
                [group_id, member_user_id, role]
            )

        messages.success(request, 'メンバーを追加しました。')
        return redirect('accounts:group_menu', group_id=group_id)
    except Exception as e:
        messages.error(request, f'メンバー追加に失敗しました: {e}')
        return redirect('accounts:group_add_member_form', group_id=group_id)

def group_menu_redirect(request):
    """レガシー互換: /groups/menu/ へのアクセスに対応（単純描画）。"""
    return render(request, 'group/group_menu.html')

def group_join_confirm(request):
    """
    GET:
      # group_member requires both member_user_id and member_id (both reference account.user_id)
                    # set member_id = member_user_id so constraints are satisfied
                    cursor.execute(
                        'INSERT INTO group_member (group_id, member_user_id, member_id, role) VALUES (%s, %s, %s, %s)',
                        [group_id, user_id, user_id, 'member']
                    )
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
            return redirect('accounts:student_login')

    # POST 処理（join/cancel）
    action = request.POST.get('action')
    if action == 'cancel':
        # 確認画面で「しない！」を押した場合は仮ホームへ戻す
        return redirect('accounts:karihome')
    if action == 'join':
        # 「はい」ボタン → グループ選択（検索）ページへ遷移
        return render(request, 'group/group_select.html', {})

    if action == 'search':
        # グループ検索フォームからの POST を受け取る（簡易実装）
        group_name = (request.POST.get('group_name') or '').strip()
        group_password = (request.POST.get('group_password') or '').strip()
        if not group_name:
            messages.error(request, 'グループ名を入力してください。')
            return render(request, 'group/group_select.html', {})

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT group_id, password, user_id FROM "group" WHERE group_name = %s', [group_name])
                row = cursor.fetchone()
                if not row:
                    # 見つからない／パスワード不一致は同じメッセージにする
                    messages.error(request, 'グループ名かパスワードが間違っています')
                    return render(request, 'group/group_select.html', {})

                found_group_id, stored_hashed, creator_user_id = row[0], row[1] or '', row[2]
                # stored_hashed が空文字ならパスワード不要（入力も空であることが期待される）
                if not stored_hashed:
                    if group_password != '':
                        messages.error(request, 'グループ名かパスワードが間違っています')
                        return render(request, 'group/group_select.html', {})
                else:
                    if not check_password(group_password, stored_hashed):
                        messages.error(request, 'グループ名かパスワードが間違っています')
                        return render(request, 'group/group_select.html', {})

                # 検索成功 → 確認ページへ遷移して内容を表示（ここでまだ group_member には入れない）
                creator_name = ''
                try:
                    with connection.cursor() as c2:
                        c2.execute('SELECT user_name FROM account WHERE user_id = %s', [creator_user_id])
                        r2 = c2.fetchone()
                        if r2:
                            creator_name = r2[0]
                except Exception:
                    creator_name = ''

                return render(request, 'group/group_check.html', {
                    'group_id': found_group_id,
                    'group_name': group_name,
                    'creator_name': creator_name,
                })

        except Exception as e:
            messages.error(request, f'グループ検索でエラーが発生しました: {e}')
            return render(request, 'group/group_select.html', {})

    if action == 'back':
        # 確認画面の戻る → 検索画面へ
        return render(request, 'group/group_select.html', {})

    if action == 'confirm_join':
        # 確認画面で加入を押した場合に実際に group_member に登録する
        try:
            found_group_id = int(request.POST.get('group_id'))
        except Exception:
            messages.error(request, 'グループ情報が不正です。')
            return redirect('accounts:account_entry')

        user_id = request.session.get('account_user_id') or (request.user.id if getattr(request.user, 'is_authenticated', False) else None)
        if user_id is None:
            messages.error(request, 'ログイン情報がありません。')
            return redirect('accounts:student_login')

        try:
            # Debugging traces removed in production
            # Use an explicit transaction to ensure both inserts/updates succeed together.
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # 重複チェックして挿入
                    cursor.execute('SELECT 1 FROM group_member WHERE group_id=%s AND member_user_id=%s', [found_group_id, user_id])
                    if not cursor.fetchone():
                        # DB schema requires both member_user_id and member_id (both reference account.user_id)
                        # ensure member_id is set to the same value as member_user_id
                        cursor.execute(
                            'INSERT INTO group_member (group_id, member_user_id, member_id, role) VALUES (%s, %s, %s, %s)',
                            [found_group_id, user_id, user_id, 'member']
                        )

                    # account テーブルの group_id を更新する
                    cursor.execute('UPDATE account SET group_id = %s WHERE user_id = %s', [found_group_id, user_id])
        # rowcount が0だと更新されていない（user_id が存在しない等）
                    if cursor.rowcount == 0:
                        # ロールバックされる（transaction.atomic のため）
                        messages.error(request, 'アカウントの更新に失敗しました（ユーザーが見つかりません）。')
                        return redirect('accounts:account_entry')
                    # Debug: 確認のため、挿入と更新の結果をその場で再取得して出力
                    try:
                        cursor.execute('SELECT id FROM group_member WHERE group_id=%s AND member_user_id=%s', [found_group_id, user_id])
                        gm = cursor.fetchone()
                    except Exception as _:
                        print('DEBUG group_join_confirm: failed to select group_member')
                    try:
                        cursor.execute('SELECT group_id FROM account WHERE user_id = %s', [user_id])
                        acc_row = cursor.fetchone()
                    except Exception as _:
                        print('DEBUG group_join_confirm: failed to select account')
        except Exception as e:
            # 何らかのエラーで失敗した場合はエラーメッセージを出す
            messages.error(request, f'グループ参加に失敗しました: {e}')
            return redirect('accounts:account_entry')

        # セッション側に group_id を入れておく（UI で参照するケースに備えて）
        try:
            request.session['account_group_id'] = found_group_id
            request.session.modified = True
        except Exception:
            pass

        messages.success(request, 'グループに参加しました。')
        try:
            return redirect('accounts:karihome')
        except Exception:
            return redirect('accounts:account_entry')

    # デフォルト: キャンセル等はアカウント画面へ
    return redirect('accounts:account_entry')


# ...existing code...


# 開発用: パスワード再設定確認テンプレートをトークンなしでプレビューする簡易ビュー
def preview_password_reset_confirm(request):
    """開発環境でテンプレート確認のために、SetPasswordForm の空フォームを渡してレンダリングするビュー。

    本番にデプロイする際はこの URL を削除してください。
    """
    form = SetPasswordForm(user=None)
    return render(request, 'accounts/password_reset_custom.html', {'form': form})

def group_delete_confirm(request, group_id):
    """グループ削除確認（暫定）。必要に応じて確認テンプレートを実装。"""
    return redirect('accounts:account_entry')


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
            return HttpResponseRedirect(reverse('password_reset_complete'))
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
    # created_at -> 初めて会った日（datetime）と累計日数・経過時間を計算してテンプレートに渡す
    created_at = account.get('created_at') if account else None
    first_met = None
    total_days_str = '0日'
    time_since_created = ''
    created_at_raw = created_at
    created_at_type = type(created_at_raw).__name__ if created_at_raw is not None else None
    days = 0
    if created_at:
        try:
            created_val = created_at
            if isinstance(created_val, str):
                dt = parse_datetime(created_val)
                if dt is None:
                    d = parse_date(created_val)
                    if d:
                        dt = datetime.datetime.combine(d, datetime.time.min)
                created_val = dt

            if created_val is not None and isinstance(created_val, datetime.datetime):
                if timezone.is_naive(created_val):
                    try:
                        created_val = timezone.make_aware(created_val, timezone.get_current_timezone())
                    except Exception:
                        created_val = timezone.make_aware(created_val, datetime.timezone.utc)
                now = timezone.now()
                delta = now - created_val
                days = max(getattr(delta, 'days', 0), 0)
                first_met = created_val
                total_days_str = f"{days}日"
                try:
                    time_since_created = format_timedelta(delta)
                except Exception:
                    time_since_created = ''
            else:
                first_met = created_at
        except Exception:
            first_met = created_at

    # ログ出力（デバッグ）
    try:
        logging.debug('t_account: created_at_raw=%s type=%s days=%s time_since_created=%s', created_at_raw, created_at_type, days, time_since_created)
    except Exception:
        pass

    return render(request, 'accounts/t_account.html', {
        'account': account,
        'user': request.user,
        'first_met': first_met,
        'total_days': total_days_str,
        'time_since_created': time_since_created,
        'created_at_raw': created_at_raw,
        'created_at_type': created_at_type,
    })
    
def account_entry(request):
    """
    account を取得し account_type に応じてテンプレートを返す。
    created_at から初めて会った日と累計日数を計算してテンプレートに渡す。
    """
    account = None
    user_id = request.session.get('account_user_id')
    email = request.session.get('account_email') or (
        getattr(request.user, 'email', None) if getattr(request.user, 'is_authenticated', False) else None
    )

    if not user_id and not email:
        return redirect('accounts:student_login')

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
            return redirect('accounts:student_login')
        account = {
            'user_id': row[0],
            'user_name': row[1],
            'email': row[2],
            'account_type': row[3],
            'age': row[4],
            'group_id': row[5],
            'created_at': row[6],
        }
        # Debug: log the raw DB row and created_at type for diagnosis
        try:
            logging.debug('account_entry: raw row=%s', row)
            logging.debug('account_entry: created_at raw=%s type=%s', row[6], type(row[6]).__name__ if row[6] is not None else None)
        except Exception:
            pass
        
    created_at = account.get('created_at')
    first_met = None
    total_days_str = "0日"
    time_since_created = ''
    if created_at:
        try:
            created_val = created_at
            # 文字列や date オブジェクトを datetime に変換する
            if isinstance(created_val, str):
                dt = parse_datetime(created_val)
                if dt is None:
                    d = parse_date(created_val)
                    if d:
                        dt = datetime.datetime.combine(d, datetime.time.min)
                created_val = dt

            # datetime.date（ただの日付）の場合は datetime に変換
            if isinstance(created_val, datetime.date) and not isinstance(created_val, datetime.datetime):
                created_val = datetime.datetime.combine(created_val, datetime.time.min)

            if created_val is not None and isinstance(created_val, datetime.datetime):
                # make timezone-aware if needed
                if timezone.is_naive(created_val):
                    try:
                        created_val = timezone.make_aware(created_val, timezone.get_current_timezone())
                    except Exception:
                        created_val = timezone.make_aware(created_val, datetime.timezone.utc)

                now = timezone.now()
                delta = now - created_val
                days = max(getattr(delta, 'days', 0), 0)
                first_met = created_val
                total_days_str = f"{days}日"
                try:
                    time_since_created = format_timedelta(delta)
                except Exception:
                    time_since_created = ''
            else:
                first_met = created_at
                total_days_str = '0日'
                time_since_created = ''
        except Exception:
            first_met = created_at
            total_days_str = '0日'
            time_since_created = ''

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

    groups = []
    current_user_id = account.get('user_id') or request.session.get('account_user_id') or (
        request.user.id if getattr(request.user, 'is_authenticated', False) else None
    )
    try:
        if current_user_id is not None:
            try:
                current_user_id = int(current_user_id)
            except Exception:
                current_user_id = None

        if current_user_id is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT g.group_id, g.user_id, g.group_name,
                           COALESCE((SELECT COUNT(*) FROM group_member gm WHERE gm.group_id = g.group_id), 0) AS member_count
                    FROM "group" g
                    WHERE g.user_id = %s
                    ORDER BY g.group_id
                    """,
                    [current_user_id]
                )
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
        'time_since_created': time_since_created,
        'groups': groups,
        'current_user_id': current_user_id,
    }
    # include created_at raw/type for template debugging
    try:
        context['created_at_raw'] = account.get('created_at')
        context['created_at_type'] = type(account.get('created_at')).__name__ if account.get('created_at') is not None else None
    except Exception:
        context['created_at_raw'] = None
        context['created_at_type'] = None

    # Cleanup: remove groups that have zero members.
    # 要求: グループ一覧の表示時、メンバーが0人のグループは DB から削除して一覧に表示しない。
    # 実装は安全に実行するためトランザクション内で行う。
    try:
        delete_ids = [g['group_id'] for g in groups if int(g.get('member_count', 0)) == 0]
        if delete_ids:
            from django.db import transaction as _transaction
            with _transaction.atomic():
                for gid in delete_ids:
                    try:
                        # 物理削除（member_count==0 のため外部キー制約は通常問題にならない想定）
                        Group.objects.filter(group_id=gid).delete()
                    except Exception:
                        # 削除に失敗しても処理を継続する（ログは残しておく）
                        logging.exception(f'failed to delete group {gid}')
            # 削除したものを groups リストから除外して context を更新
            groups = [g for g in groups if int(g.get('member_count', 0)) > 0]
            context['groups'] = groups
    except Exception:
        # 削除ロジックで致命的エラーが起きてもビューの表示は継続させる
        logging.exception('cleanup of zero-member groups failed')
    # 参加グループ情報を account.group_id から取得して context に含める
    joined_group = None
    try:
        gid = account.get('group_id')
        if gid:
            with connection.cursor() as cursor:
                cursor.execute('SELECT group_id, group_name, user_id FROM "group" WHERE group_id = %s', [gid])
                g = cursor.fetchone()
                if g:
                    creator_name = ''
                    try:
                        with connection.cursor() as c2:
                            c2.execute('SELECT user_name FROM account WHERE user_id = %s', [g[2]])
                            r = c2.fetchone()
                            if r:
                                creator_name = r[0]
                    except Exception:
                        creator_name = ''
                    joined_group = {'group_id': g[0], 'group_name': g[1], 'creator_name': creator_name}
    except Exception:
        joined_group = None

    context['joined_group'] = joined_group

    if account.get('account_type') == 'teacher':
        return render(request, 'accounts/t_account.html', context)
    return render(request, 'accounts/s_account.html', context)

def group_detail(request, group_id):
    """グループ詳細。メンバー一覧、スレッド一覧を表示。"""
    owner = _get_write_owner(request)
    if owner is None:
        messages.error(request, 'ログインが必要です')
        return redirect('accounts:student_login')

    # グループと権限のチェック
    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    try:
        membership = GroupMember.objects.get(
            group=group,
            member=owner
        )
    except GroupMember.DoesNotExist:
        return HttpResponseForbidden('このグループにアクセスする権限がありません')

    # グループメンバー一覧を取得
    members = GroupMember.objects.filter(
        group=group,
        is_active=True
    ).select_related('member')

    # グループに関連するスレッドを取得（後で実装）
    threads = []  # ChatThread.objects.filter(group=group).order_by('-created_at')

    return render(request, 'codemon/group_detail.html', {
        'group': group,
        'membership': membership,
        'members': members,
        'threads': threads,
        'is_teacher': owner.type == 'teacher'
    })

def group_invite(request, group_id):
    """グループにメンバーを招待（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを招待できます')

    # メールアドレスまたはユーザーIDで招待
    identifier = request.POST.get('identifier', '').strip()
    role = request.POST.get('role', 'student')

    if not identifier:
        return JsonResponse({'error': 'メールアドレスまたはユーザーIDを入力してください'}, status=400)

    try:
        # メールアドレスかユーザーIDで検索
        if '@' in identifier:
            member = Account.objects.get(email=identifier)
        else:
            member = Account.objects.get(user_id=identifier)

        # 既存メンバーシップの確認
        membership, created = GroupMember.objects.get_or_create(
            group=group,
            member=member,
            defaults={'role': role}
        )

        if not created:
            # すでにメンバーであれば重複扱いとする
            return JsonResponse({
                'error': f'{member.user_name}は既にグループのメンバーです'
            }, status=400)

        return JsonResponse({
            'status': 'ok',
            'message': f'{member.user_name}をグループに招待しました',
            'member': {
                'id': member.user_id,
                'name': member.user_name,
                'role': role
            }
        })

    except Account.DoesNotExist:
        return JsonResponse({
            'error': '指定されたユーザーが見つかりません'
        }, status=404)

def group_remove_member(request, group_id, member_id):
    """グループからメンバーを削除（教師のみ）"""
    owner = _get_write_owner(request)
    if owner is None or owner.type != 'teacher':
        return HttpResponseForbidden('教師権限が必要です')

    group = get_object_or_404(Group, group_id=group_id, is_active=True)
    if group.owner != owner:
        return HttpResponseForbidden('グループのオーナーのみメンバーを削除できます')
    
    # only accept POST for deletions
    if request.method != 'POST':
        return redirect('accounts:group_menu', group_id=group_id)

    try:
        membership = GroupMember.objects.get(
            group=group,
            member_id=member_id
        )
        # 比較はオブジェクト同士の比較が期待されるが、念のため user_id ベースでも確認する
        try:
            is_owner = (membership.member == group.owner) or (getattr(membership.member, 'user_id', None) == getattr(group, 'user_id', None))
        except Exception:
            is_owner = (membership.member == group.owner)

        if is_owner:
            # 非同期要求なら JSON、通常フォーム送信ならメッセージを出してリダイレクト
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'グループのオーナーは削除できません'}, status=400)
            messages.error(request, 'グループのオーナーは削除できません')
            return redirect('accounts:group_menu', group_id=group_id)
        # 物理削除して互換性を取る（既存スキーマに is_active がないため）
        member_name = getattr(membership.member, 'user_name', str(member_id))
        # 連携用の値を退避してから削除
        try:
            joined_at_val = None
            if hasattr(membership, 'joined_at') and membership.joined_at:
                joined_at_val = membership.joined_at
            elif hasattr(membership, 'created_at') and membership.created_at:
                joined_at_val = membership.created_at
            # メンバー削除（ORM）
            membership.delete()
        except Exception:
            # 削除に失敗したらエラーハンドリング
            logging.exception('failed to delete GroupMember')
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'メンバーの削除に失敗しました'}, status=500)
            messages.error(request, 'メンバーの削除に失敗しました')
            return redirect('accounts:group_menu', group_id=group_id)

        # 追加: account テーブルの該当ユーザーの group_id をクリアする（NULL にする）
        try:
            # まず ORM で試す
            try:
                Account.objects.filter(user_id=member_id).update(group_id=None)
            except Exception:
                # フォールバックで生 SQL を実行
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE account SET group_id = NULL WHERE user_id = %s', [member_id])
        except Exception:
            logging.exception('failed to clear account.group_id for user %s', member_id)

        # レスポンス: AJAX の場合は JSON を返し、通常はグループメニューへリダイレクト
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # 日付を文字列に整形して返す（存在すれば）
            joined_str = None
            try:
                if joined_at_val:
                    joined_str = joined_at_val.strftime('%Y/%m/%d')
            except Exception:
                joined_str = None
            return JsonResponse({'status': 'ok', 'message': f'{member_name}をグループから削除しました', 'member_id': member_id, 'member_name': member_name, 'joined_at': joined_str})

        messages.success(request, f'{member_name}をグループから削除しました')
        return redirect('accounts:group_menu', group_id=group_id)

    except GroupMember.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': '指定されたメンバーが見つかりません'}, status=404)
        messages.error(request, '指定されたメンバーが見つかりません')
        return redirect('accounts:group_menu', group_id=group_id)

def format_timedelta(delta: datetime.timedelta) -> str:
    """timedelta を受け取り日本語の経過時間表現を返す。"""
    try:
        seconds = int(delta.total_seconds())
    except Exception:
        return ''
    if seconds <= 0:
        return '0秒前'
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    if days > 0:
        if hours > 0:
            return f"{days}日{hours}時間前"
        return f"{days}日前"
    if hours > 0:
        if minutes > 0:
            return f"{hours}時間{minutes}分前"
        return f"{hours}時間前"
    if minutes > 0:
        return f"{minutes}分{sec}秒前"
    return f"{sec}秒前"