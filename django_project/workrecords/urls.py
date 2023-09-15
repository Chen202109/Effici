from django.urls import path

from . import views

urlpatterns = [
    #path('', views.workrecords),
    path('select',views.select),
    path('analysisselect',views.analysisselect),
]