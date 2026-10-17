from django.urls import path

from . import views

app_name = 'coverage'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('immunizations/', views.record_list, name='record_list'),
    path('immunizations/new/', views.record_create, name='record_create'),
    path('immunizations/<int:pk>/edit/', views.record_update, name='record_update'),
    path('immunizations/<int:pk>/delete/', views.record_delete, name='record_delete'),
    path('maternal-visits/', views.visit_list, name='visit_list'),
]