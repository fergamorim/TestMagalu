from django.urls import path
from .views import (
    RegisterView,
    CustomerListCreateView,
    CustomerDetailView,
    ImportProductsView,
    FavoriteProductListView,
    FavoriteProductDetailView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Autenticação
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Customers
    path('customers/', CustomerListCreateView.as_view(), name='Customer-list-create'),
    path('customers/<int:id>/', CustomerDetailView.as_view(), name='Customer-detail'),

    #Importar produtos
    path('import-products/', ImportProductsView.as_view(), name='import-products'),
    
    # Produtos Favoritos
    path('customers/<int:Customer_id>/favorites/', FavoriteProductListView.as_view(), name='favorite-list'),
    path('customers/<int:customer_id>/favorites/<int:product_id>/', FavoriteProductDetailView.as_view(), name='favorite-detail'),
]