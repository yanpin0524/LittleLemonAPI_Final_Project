from django.urls import path
from . import views

urlpatterns = [
    path("menu-items", views.menu_items),
    path("menu-items/<int:id>", views.single_menu_item),
    path("groups/manager/users", views.manager_users),
    path("groups/manager/users/<int:id>", views.remove_manager_user),
    path("groups/delivery-crew/users", views.delivery_users),
    path("groups/delivery-crew/users/<int:id>", views.remove_delivery_user),
    path("cart/menu-items", views.user_cart),
    path("orders", views.orders),
    path("orders/<int:id>", views.single_order),
]
