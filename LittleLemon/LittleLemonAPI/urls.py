from django.urls import path
from . import views

urlpatterns = [
    path("menu-items", views.menu_items),
    path("menu-items/<int:id>", views.single_menu_item)
]
