from django.urls import path
from rest_framework.authtoken import views as auth_views


urlpatterns = [
    path("login/", auth_views.obtain_auth_token, name="Login"),
]
