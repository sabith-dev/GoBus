from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list_view, name='review_list'),
    path('create/<uuid:booking_id>/', views.review_create_view, name='review_create'),
    path('<int:review_id>/', views.review_detail_view, name='review_detail'),
]
