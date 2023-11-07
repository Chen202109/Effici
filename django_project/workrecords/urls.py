from django.urls import path

from . import views

urlpatterns = [
    #path('', views.workrecords),
    path('select',views.select),
    path('analysisselect',views.analysisselect),
    path('analysis_service_upgrade_trend',views.analysis_service_upgrade_trend),
]