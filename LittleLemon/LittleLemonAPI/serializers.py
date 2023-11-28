from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Category, MenuItem, Cart
from django.contrib.auth.models import User, Group


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]
        extra_kwargs = {
            "slug": {"validators": [UniqueValidator(queryset=MenuItem.objects.all())]},
            "title": {"validators": [UniqueValidator(queryset=MenuItem.objects.all())]},
        }


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_id"]
        depth = 1
        extra_kwargs = {
            "title": {"validators": [UniqueValidator(queryset=MenuItem.objects.all())]},
            "price": {"min_value": 1},
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = ["user_set"]
#         depth = 1


# class TokenSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Token
#         fields = ["key", "created", "user_id"]


class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
            "user_id",
            "menuitem_id",
        ]
        depth = 1
        extra_kwargs = {
            "quantity": {"min_value": 1},
            "unit_price": {"min_value": 1},
            "price": {"min_value": 1},
        }
