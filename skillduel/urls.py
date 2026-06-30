from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("skillduel/create", views.create_duel_view, name="create_duel"),
    path("skillduel/<int:duel_id>", views.duel_arena_view, name="duel_arena"),
    path("skillduel/<int:duel_id>/result", views.duel_result_view, name="duel_result"),
    path("skillduel/leaderboard", views.leaderboard_view, name="leaderboard"),
    path("skillduel/inbox", views.inbox_view, name="inbox"),
    path("profile/<str:username>", views.profile_view, name="profile"),
]
