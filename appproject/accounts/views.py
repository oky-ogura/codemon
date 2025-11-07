from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import TeacherSignupForm
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth import logout as auth_logout
from django.db import connection


def teacher_signup(request):
    if request.method == 'POST':
        form = TeacherSignupForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # パスワードをハッシュ化して保存
            instance.password = make_password(form.cleaned_data.get('password1'))
            instance.save()
            # 登録後はログインページへリダイレクト
            return redirect('teacher_login')
    else:
        form = TeacherSignupForm()
    return render(request, 'accounts/t_signup.html', {'form': form})

def student_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/s_signup.html', {'form': form})

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('teacher_home')  # ログイン後の遷移先を適宜変更
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'accounts/t_login.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_home')  # ログイン後の遷移先を適宜変更
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')
    return render(request, 'accounts/s_login.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # ログアウト後の遷移先を適宜変更

def account_view(request):
    # groups の取得はプロジェクトに合わせて変更してください
    try:
        groups = request.user.groups.all()
    except Exception:
        groups = []
    return render(request, 'accounts/t_account.html', {'groups': groups})

def account_view(request):
    # groups の取得はプロジェクトに合わせて変更してください
    try:
        groups = request.user.groups.all()
    except Exception:
        groups = []
    return render(request, 'accounts/t_account.html', {'groups': groups})

def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()
        members = request.POST.getlist('members')  # ["id|name", ...]
        # TODO: 実際のモデル保存処理があればここで行う
        # 現状は受け取ってダッシュボードへリダイレクトするだけ
        return redirect('account_dashboard')
    return render(request, 'group/create_group.html', {})


def add_member_popup(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '').strip()
        member_name = request.POST.get('member_name', '').strip()
        params = urlencode({'id': member_id, 'name': member_name})
        return redirect(reverse('group_create') + f'?{params}')
    # ファイル名を add_group.html に合わせる
    return render(request, 'group/add_group.html', {})

def group_menu(request):
    return render(request, 'group/group_menu.html', {})

def s_account_view(request):
    # 必要ならここでユーザー情報を取得して context に入れる
    context = {}
    return render(request, 'accounts/s_account.html', context)

def user_logout(request):
    """
    POST で呼ばれたら:
      - account テーブルからログイン中のアカウントを削除（できる方法で試行）
      - セッション logout
      - logged_out テンプレートを返す
    GET の場合はアカウント画面へリダイレクト
    """
    if request.method == 'POST':
        user = request.user

        # まず models.Account があれば ORM で削除を試みる
        try:
            from .models import Account
            if hasattr(user, 'email') and user.email:
                Account.objects.filter(email=user.email).delete()
            else:
                Account.objects.filter(user_id=getattr(user, 'id', None)).delete()
        except Exception:
            # 失敗したら生 SQL で削除を試みる（メールがある場合は email で、なければ user_id で）
            try:
                with connection.cursor() as cursor:
                    if hasattr(user, 'email') and user.email:
                        cursor.execute("DELETE FROM account WHERE email = %s", [user.email])
                    else:
                        cursor.execute("DELETE FROM account WHERE user_id = %s", [getattr(user, 'id', None)])
            except Exception:
                # 削除に失敗しても続行してログアウト
                pass

        # Django ログアウト（セッション破棄）
        auth_logout(request)
        return render(request, 'accounts/logged_out.html', {})

    # GET は戻す（確認はフロントで行うため）
    return redirect('s_account')
# ...existing code...

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

def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()
        members = request.POST.getlist('members')  # ["id|name", ...]
        # TODO: 実際のモデル保存処理があればここで行う
        # 現状は受け取ってダッシュボードへリダイレクトするだけ
        return redirect('account_dashboard')
    return render(request, 'group/create_group.html', {})


def add_member_popup(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '').strip()
        member_name = request.POST.get('member_name', '').strip()
        params = urlencode({'id': member_id, 'name': member_name})
        return redirect(reverse('group_create') + f'?{params}')
    # ファイル名を add_group.html に合わせる
    return render(request, 'group/add_group.html', {})

def group_menu(request):
    return render(request, 'group/group_menu.html', {})

def s_account_view(request):
    # 必要ならここでユーザー情報を取得して context に入れる
    context = {}
    return render(request, 'accounts/s_account.html', context)

def user_logout(request):
    """
    POST で呼ばれたら:
      - account テーブルからログイン中のアカウントを削除（できる方法で試行）
      - セッション logout
      - logged_out テンプレートを返す
    GET の場合はアカウント画面へリダイレクト
    """
    if request.method == 'POST':
        user = request.user

        # まず models.Account があれば ORM で削除を試みる
        try:
            from .models import Account
            if hasattr(user, 'email') and user.email:
                Account.objects.filter(email=user.email).delete()
            else:
                Account.objects.filter(user_id=getattr(user, 'id', None)).delete()
        except Exception:
            # 失敗したら生 SQL で削除を試みる（メールがある場合は email で、なければ user_id で）
            try:
                with connection.cursor() as cursor:
                    if hasattr(user, 'email') and user.email:
                        cursor.execute("DELETE FROM account WHERE email = %s", [user.email])
                    else:
                        cursor.execute("DELETE FROM account WHERE user_id = %s", [getattr(user, 'id', None)])
            except Exception:
                # 削除に失敗しても続行してログアウト
                pass

        # Django ログアウト（セッション破棄）
        auth_logout(request)
        return render(request, 'accounts/logged_out.html', {})

    # GET は戻す（確認はフロントで行うため）
    return redirect('s_account')
# ...existing code...

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

