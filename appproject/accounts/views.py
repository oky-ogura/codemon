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
from django.http import HttpResponseRedirect, FileResponse, HttpResponseForbidden, JsonResponse
# helper from codemon app to resolve the effective Account-like owner for write operations
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

from django.db import connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from codemon.models import System, Algorithm, SystemElement
import json



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
            # ログイン成功後は仮ホーム（karihome.html）を表示する
            return render(request, 'accounts/karihome.html')
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
    return redirect('accounts:accounts_root')

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
    """
    アルゴリズム作成・編集画面
    - URLパラメータ id があれば編集モード: 既存アルゴリズム情報を取得してテンプレートに渡す
    - id がなければ新規作成モード
    """
    algorithm_id = request.GET.get('id')
    context = {}
    
    if algorithm_id:
        try:
            algorithm = Algorithm.objects.get(algorithm_id=algorithm_id)
            context = {
                'algorithm_id': algorithm.algorithm_id,
                'algorithm_name': algorithm.algorithm_name,
                'algorithm_description': algorithm.algorithm_description or '',
                'blockly_xml': algorithm.blockly_xml or '',
            }
        except Algorithm.DoesNotExist:
            messages.error(request, '指定されたアルゴリズムが見つかりません。')
    
    return render(request, 'block/index.html', context)

def system_index(request):
    """
    システム作成・編集画面
    - URLパラメータ id があれば編集モード: 既存システム情報を取得してテンプレートに渡す
    - id がなければ新規作成モード
    """
    system_id = request.GET.get('id')
    context = {}
    
    # ログインユーザーの他のシステム一覧を取得
    account = get_logged_account(request)
    other_systems_json = '[]'
    if account:
        try:
            other_systems_qs = System.objects.filter(user=account).order_by('-created_at')
            # 編集モードの場合は、編集中のシステムを除外
            if system_id:
                other_systems_qs = other_systems_qs.exclude(system_id=system_id)
            
            # JSON形式に変換
            other_systems_list = []
            for sys in other_systems_qs:
                other_systems_list.append({
                    'system_id': sys.system_id,
                    'system_name': sys.system_name
                })
            
            other_systems_json = json.dumps(other_systems_list, ensure_ascii=False)
        except Exception:
            pass
    
    context['other_systems_json'] = other_systems_json
    
    if system_id:
        try:
            system = System.objects.get(system_id=system_id)
            context['system_id'] = system.system_id
            context['system_name'] = system.system_name
            context['system_description'] = system.system_description or ''
            
            # システム要素を取得してJSON化
            elements = SystemElement.objects.filter(system=system).order_by('sort_order', 'element_id')
            elements_list = []
            for elem in elements:
                elements_list.append({
                    'element_type': elem.element_type,
                    'element_label': elem.element_label or '',
                    'element_value': elem.element_value or '',
                    'position_x': elem.position_x,
                    'position_y': elem.position_y,
                    'width': elem.width,
                    'height': elem.height,
                    'style_data': elem.style_data or {},
                    'element_config': elem.element_config or {}
                })
            context['elements_json'] = json.dumps(elements_list, ensure_ascii=False)
        except System.DoesNotExist:
            messages.error(request, '指定されたシステムが見つかりません。')
    
    return render(request, 'system/index.html', context)

# システム要素取得API
def get_system_elements(request):
    """
    指定されたシステムの要素データをJSON形式で返すAPIエンドポイント
    """
    system_id = request.GET.get('system_id')
    if not system_id:
        return JsonResponse({'error': 'system_id is required'}, status=400)
    
    account = get_logged_account(request)
    if not account:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # システムの所有者確認
        system = System.objects.get(system_id=system_id, user=account)
        
        # システム要素を取得
        elements = SystemElement.objects.filter(system=system).order_by('sort_order', 'element_id')
        elements_list = []
        for elem in elements:
            elements_list.append({
                'element_type': elem.element_type,
                'element_label': elem.element_label or '',
                'element_value': elem.element_value or '',
                'position_x': elem.position_x,
                'position_y': elem.position_y,
                'width': elem.width,
                'height': elem.height,
                'style_data': elem.style_data or {},
                'element_config': elem.element_config or {}
            })
        
        return JsonResponse({
            'success': True,
            'system_name': system.system_name,
            'elements': elements_list
        })
    except System.DoesNotExist:
        return JsonResponse({'error': 'System not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
    if request.method == 'POST':
        # POSTデータを取得
        system_name = request.POST.get('system_name', '').strip()
        system_detail = request.POST.get('system_detail', '').strip()
        created_at_str = request.POST.get('created_at', '')
        system_id = request.POST.get('system_id', '').strip()  # 編集モードの場合にシステムIDが送信される
        elements_json = request.POST.get('elements_data', '')  # 要素データ（JSON形式）
        
        # バリデーション
        if not system_name or not system_detail:
            messages.error(request, 'システム名とシステムの詳細は必須項目です。')
            return render(request, 'system/system_create.html')
        
        # ログインユーザーを取得
        account = get_logged_account(request)
        if not account:
            messages.error(request, 'ログインが必要です。')
            return redirect('accounts:student_login')
        
        try:
            if system_id:
                # 編集モード: 既存システムを更新
                system = System.objects.get(system_id=system_id, user=account)
                system.system_name = system_name
                system.system_description = system_detail
                system.save()
                # 既存の要素を削除
                SystemElement.objects.filter(system=system).delete()
                messages.success(request, f'システム「{system_name}」を更新しました。')
            else:
                # 新規作成モード: 新しいSystemオブジェクトを作成
                system = System.objects.create(
                    user=account,
                    system_name=system_name,
                    system_description=system_detail
                )
                messages.success(request, f'システム「{system_name}」を保存しました。')
            
            # 要素データを解析して保存
            if elements_json:
                try:
                    elements_data = json.loads(elements_json)
                    for idx, elem in enumerate(elements_data):
                        SystemElement.objects.create(
                            system=system,
                            element_type=elem.get('element_type', ''),
                            element_label=elem.get('element_label', ''),
                            element_value=elem.get('element_value', ''),
                            position_x=elem.get('position_x', 0),
                            position_y=elem.get('position_y', 0),
                            width=elem.get('width'),
                            height=elem.get('height'),
                            style_data=elem.get('style_data'),
                            element_config=elem.get('element_config'),
                            sort_order=idx
                        )
                except json.JSONDecodeError as e:
                    messages.warning(request, f'要素データの解析に失敗しました: {str(e)}')
                except Exception as e:
                    messages.warning(request, f'要素の保存に失敗しました: {str(e)}')
            
            # 保存完了画面へリダイレクト
            return redirect('accounts:system_save')
        except System.DoesNotExist:
            messages.error(request, '指定されたシステムが見つかりません。')
            return render(request, 'system/system_create.html')
        except Exception as e:
            messages.error(request, f'システムの保存に失敗しました: {str(e)}')
            return render(request, 'system/system_create.html')
    
    # GETリクエストの場合: 他のシステム一覧を取得してテンプレートに渡す
    account = get_logged_account(request)
    other_systems = []
    if account:
        try:
            # ログインユーザーの全システムを取得（編集中のシステムは除外する必要があるが、ここでは全て取得）
            other_systems = System.objects.filter(user=account).order_by('-created_at')
        except Exception:
            pass
    
    return render(request, 'system/system_create.html', {'other_systems': other_systems})

# システム一覧画面
def system_list(request):
    # ログインしている Account に紐づくシステムを優先して表示
    try:
        account = get_logged_account(request)
    except Exception:
        account = None

    if account:
        # 更新日が新しい順、同じ場合は作成日が新しい順
        systems = System.objects.filter(user=account).order_by('-updated_at', '-created_at')
    else:
        # ログイン情報が取れない場合は全件を上位表示（最大100件）
        systems = System.objects.all().order_by('-updated_at', '-created_at')[:100]

    return render(request, 'system/system_list.html', {'systems': systems})

# システム一覧データ取得API（一覧更新ボタン用）
def system_list_data(request):
    try:
        account = get_logged_account(request)
    except Exception:
        account = None

    if account:
        # 更新日が新しい順、同じ場合は作成日が新しい順
        systems = System.objects.filter(user=account).order_by('-updated_at', '-created_at')
    else:
        systems = System.objects.all().order_by('-updated_at', '-created_at')[:100]

    # システムデータをJSON形式に変換
    systems_data = []
    for s in systems:
        # Windowsでも動作するよう、%-を使わない形式に変更
        created_str = s.created_at.strftime('%Y年%m月%d日 %H:%M').replace('月0', '月').replace('日0', '日') if s.created_at else ''
        updated_str = s.updated_at.strftime('%Y年%m月%d日 %H:%M').replace('月0', '月').replace('日0', '日') if s.updated_at else ''
        
        systems_data.append({
            'system_id': s.system_id,
            'system_name': s.system_name,
            'system_description': s.system_description or '',
            'created_at': created_str,
            'updated_at': updated_str,
        })

    return JsonResponse({'systems': systems_data})

# 該当システム詳細画面
def system_details(request):
    # URLパラメータからシステムIDを取得
    system_id = request.GET.get('id')
    
    if not system_id:
        messages.error(request, 'システムIDが指定されていません。')
        return redirect('accounts:system_list')
    
    try:
        # システムIDでデータベースから取得
        system = System.objects.get(system_id=system_id)
        
        # ログインユーザーを取得
        account = get_logged_account(request)
        
        # 自分のシステムかどうか確認（セキュリティ）
        if account and system.user.user_id != account.user_id:
            messages.error(request, 'このシステムにアクセスする権限がありません。')
            return redirect('accounts:system_list')
        
        # システムに紐づく要素を取得
        elements = SystemElement.objects.filter(system=system).order_by('sort_order', 'element_id')
        
        # テンプレートにシステム情報を渡す
        context = {
            'system': system,
            'system_id': system.system_id,
            'system_name': system.system_name,
            'system_description': system.system_description,
            'created_at': system.created_at,
            'elements': elements,
        }
        return render(request, 'system/system_details.html', context)
        
    except System.DoesNotExist:
        messages.error(request, '指定されたシステムが見つかりませんでした。')
        return redirect('accounts:system_list')
    except Exception as e:
        messages.error(request, f'エラーが発生しました: {str(e)}')
        return redirect('accounts:system_list')

# システム削除確認画面
def system_delete(request):
    # URLパラメータからシステムIDを取得
    system_id = request.GET.get('id')
    
    if not system_id:
        messages.error(request, 'システムIDが指定されていません。')
        return redirect('accounts:system_list')
    
    try:
        # システムIDでデータベースから取得
        system = System.objects.get(system_id=system_id)
        
        # ログインユーザーを取得
        account = get_logged_account(request)
        
        # 自分のシステムかどうか確認（セキュリティ）
        if account and system.user.user_id != account.user_id:
            messages.error(request, 'このシステムを削除する権限がありません。')
            return redirect('accounts:system_list')
        
        # POSTリクエストの場合は削除を実行
        if request.method == 'POST':
            system_name = system.system_name
            system.delete()
            messages.success(request, f'システム「{system_name}」を削除しました。')
            return redirect('accounts:system_delete_success')
        
        # GETリクエストの場合は削除確認画面を表示
        context = {
            'system': system,
            'system_id': system.system_id,
            'system_name': system.system_name,
            'system_description': system.system_description,
            'created_at': system.created_at,
        }
        return render(request, 'system/system_delete.html', context)
        
    except System.DoesNotExist:
        messages.error(request, '指定されたシステムが見つかりませんでした。')
        return redirect('accounts:system_list')
    except Exception as e:
        messages.error(request, f'エラーが発生しました: {str(e)}')
        return redirect('accounts:system_list')

# システム削除完了画面
def system_delete_success(request):
    return render(request, 'system/system_delete_success.html')

# システムチュートリアル画面
def system_tutorial(request):

    return render(request, 'system/system_tutorial.html')


# アルゴリズム選択画面
def block_choice(request):
    """
    /accounts/block/choice/ で block/choice.html を表示する簡易ビュー
    """
    return render(request, 'block/block_choice.html')

# 新規アルゴリズム作成画面
def block_create(request):
    """
    アルゴリズム名・概要を入力して保存する画面
    - GETリクエスト: フォームを表示
    - POSTリクエスト: データベースに保存または更新
    """
    if request.method == 'POST':
        algorithm_name = request.POST.get('algorithm_name', '').strip()
        algorithm_description = request.POST.get('algorithm_description', '').strip()
        algorithm_id = request.POST.get('algorithm_id', '').strip()
        blockly_xml = request.POST.get('blockly_xml', '').strip()
        
        # バリデーション
        if not algorithm_name:
            messages.error(request, 'アルゴリズム名は必須項目です。')
            return render(request, 'block/block_create.html', {
                'algorithm_name': algorithm_name,
                'algorithm_description': algorithm_description,
            })
        
        try:
            # ログインユーザーを取得
            account = get_logged_account(request)
            
            if algorithm_id:
                # 既存のアルゴリズムを更新
                algorithm = Algorithm.objects.get(algorithm_id=algorithm_id, user=account)
                algorithm.algorithm_name = algorithm_name
                algorithm.algorithm_description = algorithm_description
                if blockly_xml:
                    algorithm.blockly_xml = blockly_xml
                algorithm.save()
            else:
                # 新規作成
                Algorithm.objects.create(
                    user=account,
                    algorithm_name=algorithm_name,
                    algorithm_description=algorithm_description,
                    blockly_xml=blockly_xml if blockly_xml else None
                )
            
            # 保存成功後はsave.htmlを表示
            return render(request, 'block/save.html')
            
        except Algorithm.DoesNotExist:
            messages.error(request, '指定されたアルゴリズムが見つかりません。')
            return redirect('accounts:block_list')
        except Exception as e:
            messages.error(request, f'保存中にエラーが発生しました: {str(e)}')
            return render(request, 'block/block_create.html', {
                'algorithm_name': algorithm_name,
                'algorithm_description': algorithm_description,
            })
    
    # GETリクエスト: フォームを表示（編集モード対応）
    algorithm_id = request.GET.get('id')
    context = {}
    
    if algorithm_id:
        try:
            algorithm = Algorithm.objects.get(algorithm_id=algorithm_id)
            context = {
                'algorithm_id': algorithm.algorithm_id,
                'algorithm_name': algorithm.algorithm_name,
                'algorithm_description': algorithm.algorithm_description or '',
                'blockly_xml': algorithm.blockly_xml or '',
            }
        except Algorithm.DoesNotExist:
            messages.error(request, '指定されたアルゴリズムが見つかりません。')
    
    return render(request, 'block/block_create.html', context)


# 該当アルゴリズム詳細画面
def block_details(request):
    # URLパラメータからアルゴリズムIDを取得
    algorithm_id = request.GET.get('id')
    
    if not algorithm_id:
        messages.error(request, 'アルゴリズムIDが指定されていません。')
        return redirect('accounts:block_list')
    
    try:
        # アルゴリズムIDでデータベースから取得
        algorithm = Algorithm.objects.get(algorithm_id=algorithm_id)
        
        # ログインユーザーを取得
        account = get_logged_account(request)
        
        # POSTリクエストの場合は更新処理
        if request.method == 'POST':
            algorithm_name = request.POST.get('algorithm_name', '').strip()
            algorithm_description = request.POST.get('algorithm_description', '').strip()
            
            # バリデーション
            if not algorithm_name:
                messages.error(request, 'アルゴリズム名は必須項目です。')
                return render(request, 'block/block_details.html', {
                    'algorithm': algorithm,
                })
            
            # 所有者チェック（他のユーザーのアルゴリズムは編集不可）
            if algorithm.user != account:
                messages.error(request, '他のユーザーのアルゴリズムは編集できません。')
                return redirect('accounts:block_list')
            
            # アルゴリズムを更新
            algorithm.algorithm_name = algorithm_name
            algorithm.algorithm_description = algorithm_description
            algorithm.save()
            
            # 成功メッセージは表示せず、一覧画面にリダイレクト
            return redirect('accounts:block_list')
        
        # GETリクエストの場合は詳細表示
        context = {
            'algorithm': algorithm,
        }
        
        return render(request, 'block/block_details.html', context)
        
    except Algorithm.DoesNotExist:
        messages.error(request, '指定されたアルゴリズムが見つかりません。')
        return redirect('accounts:block_list')
    except Exception as e:
        messages.error(request, f'エラーが発生しました: {str(e)}')
        return redirect('accounts:block_list')

# アルゴリズム一覧画面
def block_list(request):
    # ログインしている Account に紐づくアルゴリズムを優先して表示
    try:
        account = get_logged_account(request)
    except Exception:
        account = None

    if account:
        # 更新日が新しい順、同じ場合は作成日が新しい順
        algorithms = Algorithm.objects.filter(user=account).order_by('-updated_at', '-created_at')
    else:
        # ログイン情報が取れない場合は全件を上位表示（最大100件）
        algorithms = Algorithm.objects.all().order_by('-updated_at', '-created_at')[:100]

    return render(request, 'block/block_list.html', {'algorithms': algorithms})

# アルゴリズム一覧データ取得API（一覧更新ボタン用）
def block_list_data(request):
    try:
        account = get_logged_account(request)
    except Exception:
        account = None

    if account:
        # 更新日が新しい順、同じ場合は作成日が新しい順
        algorithms = Algorithm.objects.filter(user=account).order_by('-updated_at', '-created_at')
    else:
        algorithms = Algorithm.objects.all().order_by('-updated_at', '-created_at')[:100]

    # アルゴリズムデータをJSON形式に変換
    algorithms_data = []
    for a in algorithms:
        # Windowsでも動作するよう、%-を使わない形式に変更
        created_str = a.created_at.strftime('%Y年%m月%d日 %H:%M').replace('月0', '月').replace('日0', '日') if a.created_at else ''
        updated_str = a.updated_at.strftime('%Y年%m月%d日 %H:%M').replace('月0', '月').replace('日0', '日') if a.updated_at else ''
        
        algorithms_data.append({
            'algorithm_id': a.algorithm_id,
            'algorithm_name': a.algorithm_name,
            'algorithm_description': a.algorithm_description or '',
            'created_at': created_str,
            'updated_at': updated_str,
        })

    return JsonResponse({'algorithms': algorithms_data})


# アルゴリズム削除確認・削除実行
def block_delete(request):
    # URLパラメータからアルゴリズムIDを取得
    algorithm_id = request.GET.get('id')
    
    if not algorithm_id:
        messages.error(request, 'アルゴリズムIDが指定されていません。')
        return redirect('accounts:block_list')
    
    try:
        # アルゴリズムIDでデータベースから取得
        algorithm = Algorithm.objects.get(algorithm_id=algorithm_id)
        
        # ログインユーザーを取得
        account = get_logged_account(request)
        
        # 自分のアルゴリズムかどうか確認（セキュリティ）
        if account and algorithm.user.user_id != account.user_id:
            messages.error(request, 'このアルゴリズムを削除する権限がありません。')
            return redirect('accounts:block_list')
        
        # POSTリクエストの場合は削除を実行
        if request.method == 'POST':
            algorithm_name = algorithm.algorithm_name
            algorithm.delete()
            messages.success(request, f'アルゴリズム「{algorithm_name}」を削除しました。')
            return redirect('accounts:block_delete_success')
        
        # GETリクエストの場合は削除確認画面を表示
        context = {
            'algorithm': algorithm,
        }
        return render(request, 'block/block_delete.html', context)
        
    except Algorithm.DoesNotExist:
        messages.error(request, '指定されたアルゴリズムが見つかりませんでした。')
        return redirect('accounts:block_list')
    except Exception as e:
        messages.error(request, f'エラーが発生しました: {str(e)}')
        return redirect('accounts:block_list')

# アルゴリズム削除完了画面
def block_delete_success(request):
    return render(request, 'block/block_delete_success.html')


# アカウントダッシュボード（生徒/教員どちらでも動作する簡易版）
def account_view(request):
    """ログインユーザーに紐づく Account を可能な限り探して適切なテンプレートを表示します。

    完全なアプリ設計では Django の User と Account を関連付ける方が望ましいですが、
    ここでは利用可能な情報で柔軟にフォールバックします。
    """
    try:
        acc = get_logged_account(request)
        if acc:
            # Delegate to account_entry which builds full context (groups, dates, etc.)
            # so that templates receive the same data structure and groups are shown.
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
    # Try to resolve the account for the current session/user
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
        try:
            now = timezone.now()
            delta = now - account.get('created_at')
            days = max(delta.days, 0)
            first_met = account.get('created_at')
            total_days_str = f"{days}日"
        except Exception:
            first_met = account.get('created_at')
            total_days_str = '0日'

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

    # Render template with gathered context (fall back to template defaults if account missing)
    return render(request, 'accounts/s_account.html', {
        'account': account,
        'first_met': first_met,
        'total_days': total_days_str,
        'joined_group': joined_group,
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
            return redirect('accounts:group_create')

        messages.success(request, 'グループを作成しました。')
        # 存在すれば group_detail に飛ばす（なければアカウントページへ）
        try:
            # Try to redirect to codemon's group_detail if it exists
            return redirect('codemon:group_detail', group_id=group_id)
        except Exception:
            # Fallback to accounts' account_entry
            return redirect('accounts:account_entry')

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
            return redirect('accounts:student_login')

    # POST 処理（join/cancel）
    action = request.POST.get('action')
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
                    messages.error(request, '該当するグループが見つかりません。')
                    return render(request, 'group/group_select.html', {})

                found_group_id, stored_hashed, creator_user_id = row[0], row[1] or '', row[2]
                # パスワードの照合:
                # - stored_hashed が空文字の場合は入力パスワードも空であることを要求する
                # - stored_hashed がある場合は check_password で検証する
                if not stored_hashed:
                    if group_password != '':
                        messages.error(request, 'パスワードが違います。')
                        return render(request, 'group/group_select.html', {})
                else:
                    if not check_password(group_password, stored_hashed):
                        messages.error(request, 'パスワードが違います。')
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
            with connection.cursor() as cursor:
                # 重複チェックして挿入
                cursor.execute('SELECT 1 FROM group_member WHERE group_id=%s AND member_user_id=%s', [found_group_id, user_id])
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO group_member (group_id, member_user_id, role) VALUES (%s, %s, %s)', [found_group_id, user_id, 'member'])
                # account テーブルの group_id を更新する
                try:
                    cursor.execute('UPDATE account SET group_id = %s WHERE user_id = %s', [found_group_id, user_id])
                except Exception:
                    # 更新失敗でも続行
                    pass
        except Exception:
            # 挿入失敗でも続行
            pass

        # セッション側に group_id を入れておく（UI で参照するケースに備えて）
        try:
            request.session['account_group_id'] = found_group_id
            request.session.modified = True
        except Exception:
            pass

        messages.success(request, 'グループに参加しました。')
        try:
            return redirect('accounts:group_detail', group_id=found_group_id)
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
    else:
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
            member=owner,
            is_active=True
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