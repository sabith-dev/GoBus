from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.route_list_view, name='route_list'),
    path('create/', views.route_create_view, name='route_create'),
    path('<int:route_id>/update/', views.route_update_view, name='route_update'),
    path('<int:route_id>/delete/', views.route_delete_view, name='route_delete'),
]
