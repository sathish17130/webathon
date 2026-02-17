from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('compare/<int:category_id>/', views.compare, name='compare'),
    path('result/<int:category_id>/', views.result, name='result'),
]
