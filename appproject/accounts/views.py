from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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
