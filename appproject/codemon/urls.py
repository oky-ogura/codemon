from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from accounts import views as accounts_views

app_name = 'codemon'

urlpatterns = [
    # 開発用レガシーURL（旧ルート）
    path('checklist_create/', views.checklist_create, name='checklist_create'),

    # ✅ これが新しいメインの一覧・選択画面
    path('checklists/selection/', views.checklist_selection, name='checklist_selection'),

    # チェックリスト一覧（復活）
    path('checklists/', views.checklist_list, name='checklist_list'),

    # 新規作成
    path('checklists/new/', views.checklist_create, name='checklist_create'),

    # 詳細表示
    path('checklists/<int:pk>/', views.checklist_detail, name='checklist_detail'),

    # 編集・保存・削除関連
    path('checklists/<int:pk>/edit/', views.checklist_edit, name='checklist_edit'),
    path('checklists/<int:pk>/save/', views.checklist_save, name='checklist_save'),
    path('checklists/<int:pk>/delete/confirm/', views.checklist_delete_confirm, name='checklist_delete_confirm'),
    path('checklists/<int:pk>/delete/', views.checklist_delete, name='checklist_delete'),

    # 項目の完了／未完了切り替え
    path('checklists/<int:pk>/items/<int:item_id>/toggle/', views.checklist_toggle_item, name='checklist_toggle_item'),

    

    # その他
    path('systems/', views.systems_list, name='systems_list'),
    path('algorithms/', views.algorithms_list, name='algorithms_list'),
    path('chat/', views.chat_view, name='chat'),
    # 投函ボックス（スレッド）管理
    path('chat/threads/', views.thread_list, name='thread_list'),
    path('chat/threads/create/', views.thread_create, name='thread_create'),
    path('chat/threads/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    # Thread messages API (JSON)
    path('chat/threads/<int:thread_id>/messages/', views.thread_messages_api, name='thread_messages_api'),
    path('chat/threads/<int:thread_id>/edit/', views.thread_edit, name='thread_edit'),
    path('chat/threads/<int:thread_id>/delete/', views.thread_delete, name='thread_delete'),
    # Upload attachments for chat (AJAX POST)
    path('chat/upload_attachments/', views.upload_attachments, name='upload_attachments'),
    # Thread actions
    path('chat/thread/<int:thread_id>/score/', views.score_thread, name='score_thread'),
    path('chat/message/<int:message_id>/score/', views.score_message, name='score_message'),
    path('chat/thread/<int:thread_id>/readers/', views.get_thread_readers, name='thread_readers'),
    # メッセージ削除
    path('chat/message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    # ダウンロード
    path('chat/attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    # メッセージ検索
    path('chat/search/', views.search_messages, name='search_messages'),
    # グループ管理
    # codemon 側には group_detail / group_invite / group_remove_member の実装が存在しないため
    # これらは accounts.views へ委譲する。名称は維持してテンプレート等の既存参照（codemon:group_detail など）を壊さない。
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', accounts_views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('groups/<int:group_id>/leave/', views.group_leave, name='group_leave'),
    path('groups/<int:group_id>/invite/', accounts_views.group_invite, name='group_invite'),
    path('groups/<int:group_id>/remove_member/<int:member_id>/', accounts_views.group_remove_member, name='group_remove_member'),
    path('', views.index, name='index'),
    path('chat/upload_attachment/', views.upload_attachments, name='upload_attachments'),
    # AI Chat API
    path('api/ai/chat', views.ai_chat_api, name='ai_chat_api'),
    path('api/ai/history', views.ai_history_api, name='ai_history_api'),
]

# 開発環境での静的ファイル配信設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
