from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page),
    path("check-user/", views.check_user),
    path("register/", views.register_page),
    path("welcome/", views.welcome_page),
    path("promo/", views.promo_page),
]
