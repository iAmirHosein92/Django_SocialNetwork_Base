from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='user_profile'),
    path('follow/<int:user_id>/', views.UserFollowView.as_view(), name='user_follow'),
    path('unfollow/<int:user_id>/', views.UserUnfollowView.as_view(), name='user_unfollow'),
    path('profile/edit/<int:user_id>/', views.EditProfileView.as_view(), name='edit_profile'),
    path('reset_password/', views.UserPasswordResetView.as_view(), name='user_password_reset'),
    path('reset_password_done/', views.UserPasswordResetDoneView.as_view(), name='user_password_reset_done'),
    path('password_confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='user_password_reset_confirm'),
    path('reset_password/complete/', views.UserPasswordResetCompleteView.as_view(), name='user_password_reset_complete'),

]