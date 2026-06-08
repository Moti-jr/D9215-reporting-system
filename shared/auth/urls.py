from django.urls import path
from shared.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.login_issue_token, name='auth-login'),
]
