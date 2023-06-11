from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserChangePasswordView, UserDetailUpdateView, UserProfileView, \
    FollowUserView, GetFollowersView, GetFollowingView, RefereshPost, RandomPost, HomeView, SearchView, DeleteUserVIew, \
    CheckUserView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('checkuser/', CheckUserView.as_view(), name='checkuser'),
    path('changepassword/<int:pk>', UserChangePasswordView.as_view(), name='changepassword'),
    path('detailupdate/<int:pk>', UserDetailUpdateView.as_view(), name="detail"),
    path('profile/<str:username>', UserProfileView.as_view(), name='profile'),
    path('follow/<str:username>', FollowUserView.as_view(), name='follow-user'),
    path('get-followers/<str:username>', GetFollowersView.as_view(), name='get-followers'),
    path('get-following/<str:username>', GetFollowingView.as_view(), name='get-following'),
    path('refereshpost/', RefereshPost.as_view(), name="refereshpost"),
    path('randompost/', RandomPost.as_view(), name="randompost"),
    path('home/', HomeView.as_view(), name="homeview"),
    path('search/<str:username>', SearchView.as_view(), name="search"),
    path('delete-user/<int:id>', DeleteUserVIew.as_view(), name="deleteuser"),

]
