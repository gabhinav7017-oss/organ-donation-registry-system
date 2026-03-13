from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Donors
    path('donors/', views.donor_list, name='donor_list'),
    path('donors/register/', views.donor_create, name='donor_create'),
    path('donors/<int:pk>/', views.donor_detail, name='donor_detail'),
    path('donors/<int:pk>/edit/', views.donor_edit, name='donor_edit'),
    path('donors/<int:pk>/delete/', views.donor_delete, name='donor_delete'),

    # Recipients
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/register/', views.recipient_create, name='recipient_create'),
    path('recipients/<int:pk>/', views.recipient_detail, name='recipient_detail'),
    path('recipients/<int:pk>/edit/', views.recipient_edit, name='recipient_edit'),
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),

    # Matches
    path('matches/', views.match_list, name='match_list'),
    path('matches/create/', views.match_create, name='match_create'),
    path('matches/auto/', views.auto_match, name='auto_match'),
    path('matches/<int:pk>/', views.match_detail, name='match_detail'),
    path('matches/<int:pk>/edit/', views.match_edit, name='match_edit'),
    path('matches/<int:pk>/delete/', views.match_delete, name='match_delete'),
]
