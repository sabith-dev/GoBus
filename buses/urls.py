from django.urls import path
from . import views

app_name = 'buses'

urlpatterns = [
    path('', views.bus_list_view, name='bus_list'),
    path('create/', views.bus_create_view, name='bus_create'),
    path('<int:bus_id>/', views.bus_detail_view, name='bus_detail'),
    path('<int:bus_id>/update/', views.bus_update_view, name='bus_update'),
    path('<int:bus_id>/delete/', views.bus_delete_view, name='bus_delete'),
]
