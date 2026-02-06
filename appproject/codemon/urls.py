from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
    # チェックリストアイテム一覧API

from accounts import views as accounts_views

app_name = 'codemon'

urlpatterns = [
    path('api/checklists/<int:checklist_id>/items/', views.get_checklist_items_api, name='get_items_api'),

    # 項目の完了／未完了切り替え（最優先でマッチさせるため一番上に移動）
    path('checklists/<int:pk>/items/<int:item_id>/toggle/', views.checklist_toggle_item, name='checklist_toggle_item'),

    # ⭐ 削除関連を詳細表示より上に移動（具体的なパスを先に）
    path('checklists/<int:pk>/delete/confirm/', views.checklist_delete_confirm, name='checklist_delete_confirm'),
    path('checklists/<int:pk>/delete/', views.checklist_delete, name='checklist_delete'),
    path('checklists/<int:pk>/delete/complete/', views.checklist_delete_complete, name='checklist_delete_complete'),

    # 開発用レガシーURL（旧ルート）
    path('checklist_create/', views.checklist_create, name='checklist_create'),

    # ✅ これが新しいメインの一覧・選択画面
    path('checklists/selection/', views.checklist_selection, name='checklist_selection'),

    # チェックリスト一覧（復活）
    path('checklists/', views.checklist_list, name='checklist_list'),

    # 新規作成
    path('checklists/new/', views.checklist_create, name='checklist_create'),

    # 詳細表示（削除関連の後に配置）
    path('checklists/<int:pk>/', views.checklist_detail, name='checklist_detail'),

    # 編集・保存関連
    path('checklists/<int:pk>/edit/', views.checklist_edit, name='checklist_edit'),
    path('checklists/<int:pk>/save/', views.checklist_save, name='checklist_save'),


    # 項目の完了／未完了切り替え
    path('checklists/<int:pk>/items/<int:item_id>/toggle2/', views.checklist_toggle_item, name='checklist_toggle_item'),

    # グループ管理
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('groups/delete/complete/', views.group_delete_complete, name='group_delete_complete'),
    path('groups/<int:group_id>/members/<int:member_id>/remove/', 
        accounts_views.group_remove_member, name='group_remove_member'),
    path('groups/<int:group_id>/leave/', views.group_leave, name='group_leave'),

    # その他
    path('systems/', views.systems_list, name='systems_list'),
    path('algorithms/', views.algorithms_list, name='algorithms_list'),
    path('chat/', views.chat_view, name='chat'),
    # 投函ボックス（スレッド）管理
    path('chat/threads/', views.thread_list, name='thread_list'),
    path('chat/threads/create/', views.thread_create, name='thread_create'),
    # 旧URLを新URLにリダイレクト
    path('chat/threads/<int:thread_id>/', views.submission_box_detail, name='thread_detail'),
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
    # メッセージ編集
    path('chat/message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    # ダウンロード
    path('chat/attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    # メッセージ検索
    path('chat/search/', views.search_messages, name='search_messages'),
    # UI demo routes for chat-related pages
    path('chat/ui/', views.chat_ui_index, name='chat_ui_index'),
    path('chat/ui/list/', views.chat_ui_list, name='chat_ui_list'),
    path('chat/ui/room/', views.chat_ui_room, name='chat_ui_room'),
    path('chat/ui/profile/', views.chat_ui_profile, name='chat_ui_profile'),
    path('chat/ui/submission/box/', views.chat_ui_submission_box, name='chat_ui_submission_box'),
    path('chat/ui/submission/submit/', views.chat_ui_submission_submit, name='chat_ui_submission_submit'),
    path('chat/ui/score/student/', views.chat_ui_score_student, name='chat_ui_score_student'),
    path('chat/ui/score/teacher/', views.chat_ui_score_teacher, name='chat_ui_score_teacher'),
    path('chat/ui/group/manage/', views.chat_ui_group_manage, name='chat_ui_group_manage'),
    
    # ========================================
    # チャット機能 - 新しいUI画面
    # ========================================
    # 生徒側
    path('chat/student/', views.chat_student, name='chat_student'),
    path('chat/student/icon-settings/', views.icon_settings_student, name='student_icon_settings'),
    path('chat/student/upload-file/', views.upload_file_student, name='upload_file'),
    path('chat/student/upload-image/', views.upload_image_student, name='upload_image'),
    path('chat/student/grades/', views.grades_view_student, name='grades_view'),
    path('chat/student/submissions/', views.submission_list_student, name='submission_list_student'),
    path('chat/group/<int:group_id>/thread/', views.group_chat_thread, name='group_chat_thread'),
    path('chat/group/<int:group_id>/messages/', views.group_chat_messages, name='group_chat_messages'),
    path('chat/thread/<int:thread_id>/messages/', views.thread_messages, name='thread_messages'),
    
    # 教師側
    path('chat/teacher/', views.chat_teacher, name='chat_teacher'),
    path('chat/teacher/icon-settings/', views.icon_settings_teacher, name='teacher_icon_settings'),
    path('chat/teacher/upload-file/', views.upload_file_teacher, name='upload_file_teacher'),
    path('chat/teacher/upload-image/', views.upload_image_teacher, name='upload_image_teacher'),
    path('chat/teacher/invitation/', views.chat_invitation, name='chat_invitation'),
    path('chat/teacher/invitation/<int:group_id>/add-member/', views.add_group_member, name='add_group_member'),
    path('chat/invite/<str:token>/', views.messege_group_invite, name='messege_group_invite'),
    path('chat/direct/<int:thread_id>/messages/', views.direct_messages, name='direct_messages'),
    path('chat/teacher/submission-box/', views.submission_box_teacher, name='submission_box'),
    path('chat/teacher/submission-box/<int:group_id>/', views.submission_box_teacher, name='submission_box_by_group'),
    path('chat/teacher/submission-box/create/', views.submission_box_create_teacher, name='submission_box_create'),
    path('chat/teacher/submission-box/<int:thread_id>/delete/', views.submission_box_delete_teacher, name='submission_box_delete'),
    path('chat/teacher/submission-box/delete/complete/', views.submission_box_delete_complete, name='submission_box_delete_complete'),
    path('chat/submission-box/<int:thread_id>/', views.submission_box_detail, name='submission_box_detail'),
    path('chat/teacher/group-management/', views.group_management_teacher, name='group_management'),
    path('chat/teacher/group-create/', views.chat_messege_group_create, name='chat_messege_group_create'),
    path('chat/teacher/group-create/submit/', views.messege_group_create, name='messege_group_create'),
    path('chat/teacher/group-edit/<int:group_id>/', views.group_edit, name='messege_group_edit'),
    path('chat/teacher/group/<int:group_id>/member/<int:member_id>/delete/', views.group_member_delete, name='group_member_delete'),
    path('chat/teacher/group/<int:group_id>/member/<int:member_id>/delete/complete/', views.group_member_delete_complete, name='group_member_delete_complete'),
    path('chat/teacher/grading/', views.grading_teacher, name='grading'),
    path('chat/teacher/grading/<int:message_id>/', views.grading_teacher, name='grading_with_message'),
    path('chat/teacher/grading/<int:message_id>/detail/', views.grading_detail_view, name='grading_detail'),
    path('chat/student/grading/<int:message_id>/detail/', views.grading_detail_student, name='grading_detail_student'),
    
    # 採点済みチェック API
    path('api/toggle-grading-check/<int:message_id>/', views.toggle_grading_check, name='toggle_grading_check'),
    
    # 既読マークAPI
    path('api/mark-messages-read/', views.mark_messages_read, name='mark_messages_read'),
    
    # アバター保存API
    path('api/save-avatar/', views.save_avatar, name='save_avatar'),
    
    # チャット機能デモインデックス
    path('chat/demo/', views.chat_demo_index, name='chat_demo_index'),
    
    path('', views.index, name='index'),
    path('chat/upload_attachment/', views.upload_attachments, name='upload_attachments'),
    # AI Chat API
    path('api/ai/chat', views.ai_chat_api, name='ai_chat_api'),
    path('api/ai/history', views.ai_history_api, name='ai_history_api'),
    
    # アクセサリー管理
    path('accessories/', views.accessory_shop, name='accessory_shop'),
    path('accessories/equip/<int:accessory_id>/', views.equip_accessory, name='equip_accessory'),
    path('accessories/unequip/', views.unequip_accessory, name='unequip_accessory'),
    path('accessories/purchase/<int:accessory_id>/', views.purchase_accessory, name='purchase_accessory'),
    
    # 実績システム
    path('achievements/', views.achievements_view, name='achievements'),
    path('achievements/claim/<int:achievement_id>/', views.claim_achievement_reward, name='claim_achievement_reward'),
    path('achievements/claim_all/', views.claim_all_achievements, name='claim_all_achievements'),
    path('achievements/clear_notifications/', views.clear_achievement_notifications, name='clear_achievement_notifications'),
]

# 開発環境での静的ファイル配信設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
