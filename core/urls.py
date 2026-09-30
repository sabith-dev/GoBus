from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('features/', views.features_view, name='features'),
    path('offers/', views.offers_view, name='offers'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('buses/search/', views.search_view, name='search'),
]