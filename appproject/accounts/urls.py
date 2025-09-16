from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('teacher_login/', auth_views.LoginView.as_view(template_name='accounts/t_login.html'), name='teacher_login'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('student_login/', auth_views.LoginView.as_view(template_name='accounts/s_login.html'), name='student_login'),
    path('student_signup/', views.student_signup, name='student_signup'),
]
