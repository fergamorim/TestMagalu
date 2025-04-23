from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, FavoriteProduct
from .serializers import CustomerSerializer, FavoriteProductSerializer, UserSerializer, TokenSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions

User = get_user_model()

class PublicEndpoint(permissions.BasePermission):
    """Permissão personalizada para endpoints públicos"""
    def has_permission(self, request, view):
        return True
    

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
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
    """
    list:
    Retorna a lista de todos os clientes cadastrados.

    create:
    Cadastra um novo cliente.

    Parâmetros:
    - name: string (obrigatório)
    - email: string (obrigatório, formato email, único)
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Lista pública de clientes (apenas leitura)",
        responses={200: CustomerSerializer(many=True)}
    )

    def perform_create(self, serializer):
        email = serializer.validated_data.get('email')
        if Customer.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Este e-mail já está cadastrado'})
        serializer.save()

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

class CustomerListView(generics.ListAPIView):
    """
    Endpoint público para listagem básica de clientes
    """
    permission_classes = [PublicEndpoint]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @swagger_auto_schema(
        operation_description="Lista pública de clientes (apenas leitura)",
        responses={200: CustomerSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class FavoriteProductListView(generics.ListCreateAPIView):
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
        Customer_id = self.kwargs.get('Customer_id')
        Customer = get_object_or_404(Customer, id=Customer_id)
        return Customer.favoritos.all()
    
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

        Customer_id = self.kwargs.get('Customer_id')
        Customer = get_object_or_404(Customer, id=Customer_id)
        product_id = serializer.validated_data.get('product_id')
        
        if Customer.favoritos.filter(product_id=product_id).exists():
            raise ValidationError({'product_id': 'Este produto já está na lista de favoritos'})
        
        serializer.save(Customer=Customer)

class FavoriteProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        Customer_id = self.kwargs.get('Customer_id')
        Customer = get_object_or_404(Customer, id=Customer_id)
        return Customer.favoritos.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs.get('product_id'))
        return obj