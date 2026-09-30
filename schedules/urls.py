from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    path('', views.schedule_list_view, name='schedule_list'),
    path('create/', views.schedule_create_view, name='schedule_create'),
    path('<int:schedule_id>/update/', views.schedule_update_view, name='schedule_update'),
    path('<int:schedule_id>/delete/', views.schedule_delete_view, name='schedule_delete'),
]
