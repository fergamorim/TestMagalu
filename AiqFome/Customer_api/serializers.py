from rest_framework import serializers
from .models import Customer, FavoriteProduct
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'date_register']
        extra_kwargs = {
            'email': {'validators': []},
        }

class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = ['id', 'product_id', 'title', 'customer', 'price', 'review', 'date_addition']
        read_only_fields = ['title', 'title', 'price', 'review']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass