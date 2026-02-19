from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("keyboard_clicked", views.keyboard_clicked, name="keyboard_clicked"),
    path("color_clicked", views.color_clicked, name="color_clicked"),
    path("backspace_clicked", views.backspace_clicked, name="backspace_clicked"),
    path("enter_clicked", views.enter_clicked, name="enter_clicked"),
    path(
        "guess_letter_clicked", views.guess_letter_clicked, name="guess_letter_clicked"
    ),
    path("new_game", views.new_game, name="new_game"),
]
