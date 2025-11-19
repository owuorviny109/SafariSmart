from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('', views.destination_list, name='list'),
    path('browse/', views.destination_browse, name='browse'),
    path('<slug:slug>/', views.destination_detail, name='detail'),
]
