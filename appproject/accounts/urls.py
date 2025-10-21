from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Redirect the accounts root to the student login page
    path('', RedirectView.as_view(url='student_login/', permanent=False), name='accounts_root'),
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_signup/', views.student_signup, name='student_signup'),
    path('logout/', views.user_logout, name='logout'),
]
