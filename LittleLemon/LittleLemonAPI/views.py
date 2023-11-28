from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart
from .serializers import (
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
)

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# Menu-Item
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        serialized_items = MenuItemSerializer(items, many=True)

        return Response(serialized_items.data, 200)
    if request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()

        return Response(serialized_item.data, 201)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def single_menu_item(request, id):
    if request.method == "GET":
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)

        return Response(serialized_item.data, 200)

    if request.method == "PUT" and request.user.groups.filter(name="Manager").exists():
        single_item = get_object_or_404(MenuItem, pk=id)
        data = request.data

        single_item.title = data.get("title", single_item.title)
        single_item.price = data.get("price", single_item.price)
        single_item.featured = data.get("featured", single_item.featured)
        single_item.category_id = data.get("category_id", single_item.category_id)

        single_item.save()
        serialized_item = MenuItemSerializer(single_item)

        return Response(serialized_item.data, 200)

    if (
        request.method == "DELETE"
        and request.user.groups.filter(name="Manager").exists()
    ):
        single_item = get_object_or_404(MenuItem, pk=id)
        single_item.delete()

        return Response({"message": "Deleted"}, 200)

    else:
        return Response({"message": "Unauthorized"}, 403)


# User-Group-Management
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manager_users(request):
    if request.user.groups.filter(name="Manager").exists():
        if request.method == "GET":
            manager_group = Group.objects.get(name="Manager")
            manager_user_set = manager_group.user_set.all()

            serialized_manger_users = UserSerializer(manager_user_set, many=True)

            return Response(serialized_manger_users.data, 200)

        if request.method == "POST":
            username = request.data["username"]
            user = get_object_or_404(User, username=username)

            manager_group = Group.objects.get(name="Manager")
            manager_group.user_set.add(user)

            return Response({"message": "Success"}, 201)

    else:
        return Response({"message": "Unauthorized"}, 403)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_manager_user(request, id):
    if (
        request.method == "DELETE"
        and request.user.groups.filter(name="Manager").exists()
    ):
        user = get_object_or_404(User, pk=id)

        manager_group = Group.objects.get(name="Manager")
        manager_group.user_set.remove(user)

        return Response({"message": "Success"})
    else:
        return Response({"message": "Unauthorized"}, 403)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def delivery_users(request):
    if request.user.groups.filter(name="Manager").exists():
        if request.method == "GET":
            delivery_group = Group.objects.get(name="Delivery-crew")
            delivery_user_set = delivery_group.user_set.all()

            serialized_delivery_users = UserSerializer(delivery_user_set, many=True)

            return Response(serialized_delivery_users.data, 200)

        if request.method == "POST":
            username = request.data["username"]
            user = get_object_or_404(User, username=username)

            delivery_group = Group.objects.get(name="Delivery-crew")
            delivery_group.user_set.add(user)

            return Response({"message": "Success"}, 201)

    else:
        return Response({"message": "Unauthorized"}, 403)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_delivery_user(request, id):
    if (
        request.method == "DELETE"
        and request.user.groups.filter(name="Manager").exists()
    ):
        user = get_object_or_404(User, pk=id)

        delivery_group = Group.objects.get(name="Delivery-crew")
        delivery_group.user_set.remove(user)

        return Response({"message": "Success"}, 200)
    else:
        return Response({"message": "Unauthorized"}, 403)


# Cart-Management
@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def user_cart(request):
    # Check the user isn't a "Manager" or "Delivery-crew"
    if not request.user.groups.filter(name__in=["Manager", "Delivery-crew"]).exists():
        if request.method == "GET":
            current_user_id = request.user.id

            cart = Cart.objects.filter(user__id=current_user_id)
            serialized_cart = CartSerializer(cart, many=True)

            return Response(serialized_cart.data, 200)
        if request.method == "POST":
            data = request.data
            data["user_id"] = request.user.id
            serialized_item = CartSerializer(data=data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()

            return Response(serialized_item.data, 201)
        if request.method == "DELETE":
            current_user_id = request.user.id
            cart = Cart.objects.filter(user__id=current_user_id)
            cart.delete()

            return Response({"message": "Deleted"}, 200)
    else:
        return Response({"message": "Unauthorized, You are not Customer."}, 403)
