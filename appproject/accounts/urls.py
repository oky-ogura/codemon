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
    path('block/', views.block_index, name='block_index'),
    path('block/save/', views.block_save, name='block_save'),
    path('system/', views.system_index, name='system_index'),
    path('system/save/', views.system_save, name='system_save'),
    path('system/choice/', views.system_choice, name='system_choice'),
    path('system/create/', views.system_create, name='system_create'),
    path('system/list/', views.system_list, name='system_list'),
    path('system/details/', views.system_details, name='system_details'),
]
