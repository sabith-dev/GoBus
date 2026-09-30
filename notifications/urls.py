from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list_view, name='notification_list'),
    path('<int:notification_id>/read/', views.notification_mark_read_view, name='notification_mark_read'),
    path('read-all/', views.notification_mark_all_read_view, name='notification_mark_all_read'),
    path('api/unread-count/', views.notification_unread_count_api, name='unread_count_api'),
]
