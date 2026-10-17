from django.urls import path

from . import views

app_name = 'health_data'

urlpatterns = [
    path('children/', views.child_list, name='child_list'),
    path('children/new/', views.child_create, name='child_create'),
    path('children/<int:pk>/', views.child_detail, name='child_detail'),
    path('children/<int:pk>/edit/', views.child_update, name='child_update'),
    path('children/<int:pk>/delete/', views.child_delete, name='child_delete'),
    path('districts/', views.district_list, name='district_list'),
    path('districts/<int:pk>/', views.district_detail, name='district_detail'),
    path('facilities/', views.facility_list, name='facility_list'),
]