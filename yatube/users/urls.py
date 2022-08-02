from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetView,
    PasswordResetDoneView,
)
from django.urls import path, reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    # Регистрация нового пользователя
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'),
    # Авторизация существующего пользователя
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'),
    # Выход из аккаунта
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'),
    # Смена пароля
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('auth:password_change_done')
        ),
        name='password_change',
    ),

    # Уведомление об удачной смене пароля
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'),
    # Сброс пароля
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('auth:password_reset_done')
        ),
        name='password_reset',
    ),
    # Уведомление об отправке письма на сброс
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
        name='password_reset_done'),
    # Ввод нового пароля по ссылке из письма
    path(
        'reset/<uidb64>/<token>//',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('auth:password_reset_complete')
        ),
        name='password_reset_confirm'),
    # Подтверждение об успешном восстановлении пароля
    path(
        'reset/down/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='password_reset_complete'),
]
