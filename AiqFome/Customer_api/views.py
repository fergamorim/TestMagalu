from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, FavoriteProduct, Product
from .serializers import CustomerSerializer, ProductSerializer, FavoriteProductSerializer, UserSerializer, TokenSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class PublicEndpoint(permissions.BasePermission):
    """Permissão personalizada para endpoints públicos"""
    def has_permission(self, request, view):
        return True

class RegisterView(APIView):
    """
        Cria um novo user da API no sistema
            POST - /api/register/
                body: 
                    {
                        "username": "usuario",
                        "password": "senha"
                    }
                Header:
                    {
                        "Content-Type": "application/json"
                    }
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registra um novo usuário no sistema",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="Usuário criado com sucesso",
                schema=TokenSerializer
            ),
            400: "Dados inválidos ou incompletos"
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerListCreateView(generics.ListCreateAPIView):
    """ Crud de cliente
    /api/customers/

        POST - Cria um novo customer (cliente) na API
            body: {
                "name": "Fernando Amorim",
                "email": "fernando.amorim@gmial.com"
            }

            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }

            Response: [{
                    "id": INTEGER
                    "name": STRING,
                    "email": STRING,
                    "date_register": DATE STRING
                }]

        GET - Obtem todos os clientes cadastrados
            Header: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }

            Response: [{
                    "id": INTEGER
                    "name": STRING,
                    "email": STRING,
                    "date_register": DATE STRING
                }]
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lista todos os clientes cadastrados",
        responses={200: CustomerSerializer(many=True)},
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Cria um novo cliente",
        request_body=CustomerSerializer,
        responses={
            201: CustomerSerializer(),
            400: "Dados inválidos ou email já cadastrado"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        email = serializer.validated_data.get('email')
        if Customer.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Este e-mail já está cadastrado'})
        serializer.save()

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Crud de cliente
    /api/customers/<int:id>/

        GET - Retorna informações do Customer (Cliente)
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                    "id": INTEGER
                    "name": STRING,
                    "email": STRING,
                    "date_register": DATE STRING
                }

        PUT - Atualiza informações do Customer (Cliente)
            Body: {
                    "name": "string",
                    "email": "user@example.com"
                }
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                    "id": INTEGER
                    "name": STRING,
                    "email": STRING,
                    "date_register": DATE STRING
                }

        PATCH - Atualiza parcialmente informações do Customer (Cliente)
            Body: {
                    "name": "string",
                    "email": "user@example.com"
                }
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                    "id": INTEGER
                    "name": STRING,
                    "email": STRING,
                    "date_register": DATE STRING
                }

        DELETE - DELETA informações do Customer (Cliente)
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response code: {
                    204	: Cliente removido com sucesso
                    404	:Cliente não encontrado
            }
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Recupera os detalhes de um cliente específico",
        responses={
            200: CustomerSerializer(),
            404: "Cliente não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza todos os campos de um cliente",
        request_body=CustomerSerializer,
        responses={
            200: CustomerSerializer(),
            400: "Dados inválidos",
            404: "Cliente não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza parcialmente um cliente",
        request_body=CustomerSerializer,
        responses={
            200: CustomerSerializer(),
            400: "Dados inválidos",
            404: "Cliente não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Remove um cliente do sistema",
        responses={
            204: "Cliente removido com sucesso",
            404: "Cliente não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class ImportProductsView(APIView):
    """ Importa produtos da API extrena
    /api/import-products/

        POST - Acrescenta ao banco de dados novos produtos da API externa
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response: {
                    "message": STRING,
                    "imported": INTEGER,
                    "skipped": INTEGER,
                    "imported_ids": [],
                    "skipped_ids": []
                }
    """
    @swagger_auto_schema(
        operation_description="Inicia a importação de produtos da API externa em background",
        responses={
            202: openapi.Response(
                description="Importação iniciada",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            503: "Serviço de importação indisponível"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, format=None):
        try:
            response = requests.get('https://fakestoreapi.com/products')
            response.raise_for_status() 
            
            products_data = response.json()
            imported_products = []
            skipped_products = []
            
            for product_data in products_data:
                if Product.objects.filter(api_id=product_data['id']).exists():
                    skipped_products.append(product_data['id'])
                    continue
                
                product = Product(
                    api_id=product_data['id'],
                    title=product_data['title'],
                    price=product_data['price'],
                    description=product_data['description'],
                    category=product_data['category'],
                    image_url=product_data['image'],
                    rating_rate=product_data['rating']['rate'],
                    rating_count=product_data['rating']['count']
                )
                product.save()
                imported_products.append(product_data['id'])
            
            return Response({
                'message': 'Importação concluída',
                'imported': len(imported_products),
                'skipped': len(skipped_products),
                'imported_ids': imported_products,
                'skipped_ids': skipped_products
            }, status=status.HTTP_201_CREATED)
            
        except requests.exceptions.RequestException as e:
            return Response({
                'error': f'Erro ao acessar a API externa: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'error': f'Erro inesperado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoriteProductListView(generics.ListCreateAPIView):
    """ Crud para adicionar e listas produtos favoritos em Customers (Cliente)
    /api/customers/<int:Customer_id>/favorites/

        POST - Cria um novo customer (cliente) na API
            body: {
                    "product_id": 1,
                    "customer": 1
                    }

            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }

            Response: {
                    "customer": 1,
                    "product_id": 1,
                    "date_addition": "2025-04-27T15:17:00.831235Z"
                }

        GET - Obtem todos os produtos favoritos de um cliente
            Header: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }

            Response: [{
                    "customer": 1,
                    "product_id": 1,
                    "date_addition": "2025-04-27T15:17:00.831235Z"
                }]
    """
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lista todos os produtos favoritos de um cliente",
        manual_parameters=[
            openapi.Parameter(
                'cliente_id',
                openapi.IN_PATH,
                description="ID do cliente",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: FavoriteProductSerializer(many=True),
            404: "Cliente não encontrado"
        }
    )

    def get_queryset(self):
        customer_id = self.kwargs.get('Customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.favoritos.all()
    
    @swagger_auto_schema(
        operation_description="Adiciona um novo produto favorito para um cliente",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID do produto na API externa"),
            },
        ),
        responses={
            201: FavoriteProductSerializer(),
            400: "Dados inválidos ou produto já existe na lista",
            404: "Cliente não encontrado"
        }
    )

    def perform_create(self, serializer):
        customer_id = self.kwargs.get('Customer_id')
        customer = get_object_or_404(Customer, id=customer_id)

        product_id = self.request.data.get('product_id')

        if not product_id:
            raise serializers.ValidationError({'product_id': 'This field is required.'})

        product = get_object_or_404(Product, id=product_id)

        if customer.favoritos.filter(product_id=product_id).exists():
            raise serializers.ValidationError({'product_id': 'Este produto já está na sua lista de favoritos.'})
        serializer.save(customer=customer, product_id=product)

class FavoriteProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ Crud de cliente
    /api/customers/<int:customer_id>/favorites/<int:product_id>/

        GET - Retorna informações de um produto favorito especifico
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                "id": INTEGER,
                "api_id": 1INTEGER,
                "title": STRING,
                "price": STRING,
                "description": STRING,
                "category": STRING,
                "image_url": STRING,
                "rating_rate": STRING,
                "rating_count": INTEGER
            }

        PUT - Atualiza produto favorito, substituindo produto ou user
            Body: {
                    "product_id": INTEGER,
                    "customer": INTEGER
                    }
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                    "product_id": INTEGER,
                    "customer": INTEGER,
                    "date_register": DATE STRING
                }

        PATCH - Atualiza parcialmente informações do Favorito
            Body: {
                    "product_id": INTEGER,
                    "customer": INTEGER
                    }
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response:{
                    "product_id": INTEGER,
                    "customer": INTEGER,
                    "date_register": DATE STRING
                }

        DELETE - Remove item favorito de cliente
            Header:{
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {{Token}}"
                }
            Response code: {
                    204	: Cliente removido com sucesso
                    404	:Cliente não encontrado
            }
    """
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'product_id'

    def get_object(self):
        customer_id = self.kwargs.get('customer_id')
        product_id = self.kwargs.get('product_id')

        favorite_product = FavoriteProduct.objects.filter(customer_id=customer_id, product_id=product_id).first()
        
        if not favorite_product:
            raise NotFound("Produto favorito não encontrado para este cliente.")

        return favorite_product

    @swagger_auto_schema(
        operation_description="Recupera os detalhes de um produto favorito específico",
        manual_parameters=[
            openapi.Parameter(
                'Customer_id',
                openapi.IN_PATH,
                description="ID do cliente",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'product_id',
                openapi.IN_PATH,
                description="ID do produto favorito",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: ProductSerializer(),
            404: "Cliente ou produto não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        favorite_product = self.get_object()
        product = favorite_product.product_id

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Atualiza os dados de um produto favorito",
        request_body=FavoriteProductSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Customer_id',
                openapi.IN_PATH,
                description="ID do cliente",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: FavoriteProductSerializer(),
            400: "Dados inválidos",
            404: "Cliente ou produto não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza parcialmente um produto favorito",
        request_body=FavoriteProductSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Customer_id',
                openapi.IN_PATH,
                description="ID do cliente",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: FavoriteProductSerializer(),
            400: "Dados inválidos",
            404: "Cliente ou produto não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Remove um produto da lista de favoritos do cliente",
        manual_parameters=[
            openapi.Parameter(
                'Customer_id',
                openapi.IN_PATH,
                description="ID do cliente",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'product_id',
                openapi.IN_PATH,
                description="ID do produto favorito",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            204: "Produto removido com sucesso",
            404: "Cliente ou produto não encontrado"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
