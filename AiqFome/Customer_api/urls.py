from django.urls import path
from .views import (
    RegisterView,
    CustomerListCreateView,
    CustomerDetailView,
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
    
    # Produtos Favoritos
    path('customers/<int:Customer_id>/favorites/', FavoriteProductListView.as_view(), name='favorite-list'),
    path('customers/<int:Customer_id>/favorites/<int:produto_id>/', FavoriteProductDetailView.as_view(), name='favorite-detail'),
]