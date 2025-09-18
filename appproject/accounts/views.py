from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

def teacher_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('teacher_login')
    else:
        form = UserCreationForm()
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
