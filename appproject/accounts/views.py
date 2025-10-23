from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import TeacherSignupForm


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


def student_home(request):
    # Simple placeholder student home
    return render(request, 'accounts/student_home.html')


def teacher_home(request):
    # Simple placeholder teacher home
    return render(request, 'accounts/teacher_home.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # ログアウト後の遷移先を適宜変更
