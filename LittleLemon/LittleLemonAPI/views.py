from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# from datetime import datetime


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
    # if the user isn't a Manager or Delivery-crew, it will be a Customer
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


# Order-Management
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == "GET":
        if request.user.groups.filter(name="Manager").exists():
            orders = Order.objects.all()
            serialized_orders = OrderSerializer(orders, many=True)

            return Response(serialized_orders.data, 200)

        elif request.user.groups.filter(name="Delivery-crew").exists():
            current_delivery_id = request.user.id
            orders = Order.objects.filter(delivery_crew__id=current_delivery_id)
            serialized_orders = OrderSerializer(orders, many=True)

            return Response(serialized_orders.data, 200)

        else:  # if the user isn't a Manager or Delivery-crew, it will be a Customer
            current_user_id = request.user.id
            orders = Order.objects.filter(user__id=current_user_id)
            serialized_orders = OrderSerializer(orders, many=True)

            return Response(serialized_orders.data, 200)
    if request.method == "POST":
        if not request.user.groups.filter(  # if the user isn't a Manager or Delivery-crew, it will be a Customer
            name__in=["Manager", "Delivery-crew"]
        ).exists():
            order_data = request.data
            order_data["user_id"] = request.user.id
            order_data["total"] = 0
            # order_data["date"] = datetime.now().date()

            serialized_order = OrderSerializer(data=order_data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            order_id = serialized_order.data.get("id")

            current_user_id = request.user.id
            cart = Cart.objects.filter(user__id=current_user_id)

            order_total = 0
            for cart_item in cart:
                order_item = {
                    "order_id": order_id,
                    "menuitem_id": cart_item.menuitem.id,
                    "quantity": cart_item.quantity,
                    "unit_price": cart_item.unit_price,
                    "price": cart_item.price,
                }

                order_total += order_item["price"]

                serialized_order_item = OrderItemSerializer(data=order_item)
                serialized_order_item.is_valid(raise_exception=True)
                serialized_order_item.save()

            cart.delete()

            serialized_order.instance.total = order_total
            serialized_order.instance.save()
            serialized_order = OrderSerializer(Order.objects.get(pk=order_id))

            return Response(serialized_order.data, 201)

        else:
            return Response({"message": "Unauthorized, You are not Customer."}, 403)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def single_order(request, id):
    if request.method == "GET":
        if not request.user.groups.filter(  # if the user isn't a Manager or Delivery-crew, it will be a Customer
            name__in=["Manager", "Delivery-crew"]
        ).exists():
            current_user_id = request.user.id
            order_items = OrderItem.objects.filter(
                order__id=id, order__user__id=current_user_id
            )

            if not order_items:
                return Response({"message": "Not found"}, 404)

            serialized_order_items = OrderItemSerializer(order_items, many=True)

            return Response(serialized_order_items.data, 200)

        else:
            return Response({"message": "Unauthorized, You are not Customer."}, 403)

    if request.method == "PATCH":
        if request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=id)
            data = request.data

            delivery_group = Group.objects.get(name="Delivery-crew")
            delivery_user_set = delivery_group.user_set.all()

            serialized_delivery_users = UserSerializer(delivery_user_set, many=True)

            is_delivery = any(
                user["id"] == data["delivery_crew_id"]
                for user in serialized_delivery_users.data
            )

            if is_delivery:
                order.delivery_crew_id = data.get(
                    "delivery_crew_id", order.delivery_crew_id
                )
            else:
                return Response({"message": "delivery_crew_id incorrect"}, 400)

            order.status = data.get("status", order.status)
            order.save()
            serialized_order = OrderSerializer(order)

            return Response(serialized_order.data, 200)

        if request.user.groups.filter(name="Delivery-crew").exists():
            order = get_object_or_404(Order, pk=id)
            data = request.data

            order.status = data.get("status", order.status)
            order.save()
            serialized_order = OrderSerializer(order)

            return Response(serialized_order.data, 200)

        else:  # if the user isn't a Manager or Delivery-crew, it will be a Customer
            current_user_id = request.user.id
            order = get_object_or_404(Order, pk=id, user__id=current_user_id)
            data = request.data

            order.total = data.get("total", order.total)
            order.date = data.get("date", order.date)
            order.save()
            serialized_order = OrderSerializer(order)

            return Response(serialized_order.data, 200)

    if request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=id)
            order.delete()
            order_items = OrderItem.objects.filter(order__id=id)
            order_items.delete()

            return Response({"message": "Deleted"}, 200)
        else:
            return Response({"message": "Unauthorized"}, 403)