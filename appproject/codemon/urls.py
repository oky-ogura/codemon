from django.urls import path
from . import views

app_name = 'codemon'

urlpatterns = [
    path('checklists/', views.checklist_list, name='checklist_list'),
    path('checklists/new/', views.checklist_create, name='checklist_create'),
    path('checklists/<int:pk>/', views.checklist_detail, name='checklist_detail'),
    path('checklists/<int:pk>/save/', views.checklist_save, name='checklist_save'),
    path('checklists/<int:pk>/delete/confirm/', views.checklist_delete_confirm, name='checklist_delete_confirm'),
    path('checklists/<int:pk>/delete/', views.checklist_delete, name='checklist_delete'),
    path('checklists/<int:pk>/items/<int:item_id>/toggle/', views.checklist_toggle_item, name='checklist_toggle_item'),
    path('systems/', views.systems_list, name='systems_list'),
    path('algorithms/', views.algorithms_list, name='algorithms_list'),
    path('chat/', views.chat_view, name='chat'),
]
