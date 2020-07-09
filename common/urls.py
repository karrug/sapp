from django.urls import path, include
from common.views import index, signup, signin, user_search, all_users, user_details, set_password, signout


urlpatterns = [
    path("", index, name='index'),
    path("signup", signup, name='signup'),
    path("login", signin, name='signin'),
    path("logout", signout, name='signout'),
    path("search", user_search, name='search'),
    path("user/all/", all_users, name='all_users'),
    path("user/<int:pk>/", user_details, name='user_details'),
    path("user/set_password/", set_password, name='set_password'),
]
