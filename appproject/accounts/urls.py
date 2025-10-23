from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'accounts'  # アプリケーション名前空間を追加

urlpatterns = [
    # Redirect the accounts root to the student login page
    path('', RedirectView.as_view(url='student_login/', permanent=False), name='accounts_root'),
    path('login/', RedirectView.as_view(url='student_login/', permanent=False), name='login'),  # デフォルトのログインURLをリダイレクト
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_signup/', views.student_signup, name='student_signup'),
    path('logout/', views.user_logout, name='logout'),
    path('student_home/', views.student_home, name='student_home'),
    path('teacher_home/', views.teacher_home, name='teacher_home'),
]
