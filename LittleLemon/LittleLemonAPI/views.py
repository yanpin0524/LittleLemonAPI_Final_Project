from .models import MenuItem
from .serializers import MenuItemSerializer

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser


# MenuItem
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializer(items, many=True)

        return Response(serialized_item.data)
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

        return Response(serialized_item.data)

    elif (
        request.method == "PUT" and request.user.groups.filter(name="Manager").exists()
    ):
        single_item = get_object_or_404(MenuItem, pk=id)
        data = request.data

        single_item.title = data.get("title", single_item.title)
        single_item.price = data.get("price", single_item.price)
        single_item.featured = data.get("featured", single_item.featured)
        single_item.category_id = data.get("category_id", single_item.category_id)

        single_item.save()
        serialized_item = MenuItemSerializer(single_item)

        return Response(serialized_item.data, 200)

    elif (
        request.method == "DELETE"
        and request.user.groups.filter(name="Manager").exists()
    ):
        single_item = get_object_or_404(MenuItem, pk=id)
        single_item.delete()

        return Response({"message": "Deleted"}, 200)

    else:
        return Response({"message": "Unauthorized"}, 403)
