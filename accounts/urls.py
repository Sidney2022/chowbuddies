from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('auth/signup', views.SignUp.as_view(), name='signup'),
    path('auth/verify-account/<token>', views.verify_otp, name='verify_otp'),
    path('auth/signin', views.SignIn.as_view(), name='signin'),
    path('auth/logout', views.SignOut.as_view(), name='signout'),


    path('auth/reset-password', views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/reset-password/<token>', views.ConfirmPasswordResetTokenView.as_view(), name='confirm_password_token'),
   
    path('auth/verify-account', views.send_verification_otp, name='send_otp'),
#    path('auth/verify-otp', views.verify_otp, name='verify_otp'),
    path('auth/otp-success', views.send_otp_success, name='otp-success'),
    path('auth/account-created', views.account_create_success, name='acct-success'),
    path('auth/link_account', views.link_account, name='link_account'),




   
]


