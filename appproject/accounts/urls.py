from django.urls import path
from . import views

urlpatterns = [
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_signup/', views.student_signup, name='student_signup'),
    path('logout/', views.user_logout, name='logout'),
    path('account/', views.account_view, name='account_dashboard'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/add_member/', views.add_member_popup, name='group_add_member'),
    path('groups/menu/', views.group_menu, name='group_menu'),
    path('s_account/', views.s_account_view, name='s_account'),
]
