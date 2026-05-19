from django.contrib import admin
from django.urls import path
from . import views  # ตัวนี้มี import views ไว้เรียบร้อย จึงไม่พังแน่นอน

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("check-user/", views.check_user, name="check_user"),
    path("register/", views.register_page, name="register_page"),
    path("welcome/", views.welcome_page, name="welcome_page"),
    path("promo/", views.promo_page, name="promo_page"),
    path("log-connect/", views.log_connect, name="log_connect"),
    path("wifi-demo/", views.wifi_demo),
    path('activate/', views.activate_wifi, name='activate_wifi'), # มาอยู่ตรงนี้ถูกที่แล้ว!
]