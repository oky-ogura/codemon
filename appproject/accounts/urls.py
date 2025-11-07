from django.urls import path
from django.views.generic import RedirectView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Redirect the accounts root to the student login page
    path('', RedirectView.as_view(url='student_login/', permanent=False), name='accounts_root'),
    path('teacher_login/', views.teacher_login, name='teacher_login'),
    path('teacher_signup/', views.teacher_signup, name='teacher_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student_signup/', views.student_signup, name='student_signup'),
    path('ai_appearance/', views.ai_appearance, name='ai_appearance'),
    path('ai_initial/', views.ai_initial_settings, name='ai_initial'),
    path('ai_initial/confirm/', views.ai_initial_confirm, name='ai_initial_confirm'),
    path('ai_initial/save/', views.ai_initial_save, name='ai_initial_save'),
    path('logout/', views.user_logout, name='logout'),

    # Password reset (send email) - use Django's built-in class-based view
    path('password_reset/',
         views.MyPasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             success_url='/accounts/password_reset/done/'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    # Confirm and complete steps for password reset flow
    path('reset/<uidb64>/<token>/',
         views.password_reset_confirm,
         name='password_reset_confirm'),
    # 開発用プレビュー: トークン不要で再設定フォームを表示（本番では削除推奨）
    path('debug/password_reset_confirm_preview/',
         views.preview_password_reset_confirm,
         name='password_reset_confirm_preview'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('block/', views.block_index, name='block_index'),
    path('block/save/', views.block_save, name='block_save'),
    path('system/', views.system_index, name='system_index'),
    path('system/save/', views.system_save, name='system_save'),
    path('system/choice/', views.system_choice, name='system_choice'),
    path('system/create/', views.system_create, name='system_create'),
    path('system/list/', views.system_list, name='system_list'),
    path('system/details/', views.system_details, name='system_details'),
    path('t_account/', views.account_view, name='account_dashboard'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/add_member/', views.add_member_popup, name='group_add_member'),
    path('groups/join_confirm/', views.group_join_confirm, name='group_join_confirm'),
    path('groups/menu/', views.group_menu, name='group_menu'),
    path('s_account/', views.s_account_view, name='s_account'),
    path('account_entry/', views.account_entry, name='account_entry'),
    path('block/choice/', views.block_choice, name='block_choice'),
    path('block/create/', views.block_create, name='block_create'),
    path('block/details/', views.block_details, name='block_details'),
    path('block/list/', views.block_list, name='block_list'),
]
