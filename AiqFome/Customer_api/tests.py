from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Customer, Product, FavoriteProduct

User = get_user_model()

class UserTests(APITestCase):
    
    def test_user_registration(self):
        url = reverse('register')
        data = {
            "username": "usuario",
            "password": "senha123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_user_registration_invalid(self):
        url = reverse('register')
        data = {
            "username": "usuario"
            # Falta o campo de senha
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CustomerTests(APITestCase):

    def setUp(self):
        # Criando um usuário e um token de autenticação
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
    
    def test_create_customer(self):
        url = reverse('customer-list')
        data = {
            "name": "Fernando Amorim",
            "email": "fernando.amorim@gmail.com"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['email'], data['email'])

    def test_create_customer_invalid_email(self):
        url = reverse('customer-list')
        data = {
            "name": "Fernando Amorim",
            "email": "invalid_email"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_customers(self):
        url = reverse('customer-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_update_customer(self):
        customer = Customer.objects.create(name="Customer", email="customer@example.com")
        url = reverse('customer-detail', args=[customer.id])
        data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['email'], data['email'])
    
    def test_delete_customer(self):
        customer = Customer.objects.create(name="Customer", email="customer@example.com")
        url = reverse('customer-detail', args=[customer.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class FavoriteProductTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name="Customer", email="customer@example.com")
        self.product = Product.objects.create(
            api_id=1, title="Product", price=10.99, description="Product description",
            category="Category", image_url="http://example.com/image.jpg", 
            rating_rate=4.5, rating_count=100
        )
    
    def test_add_favorite_product(self):
        url = reverse('favorite-product-list', kwargs={'Customer_id': self.customer.id})
        data = {
            "product_id": self.product.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(response.data['product_id'], self.product.id)

    def test_add_favorite_product_duplicate(self):
        FavoriteProduct.objects.create(customer=self.customer, product_id=self.product)
        url = reverse('favorite-product-list', kwargs={'Customer_id': self.customer.id})
        data = {
            "product_id": self.product.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_favorite_products(self):
        FavoriteProduct.objects.create(customer=self.customer, product_id=self.product)
        url = reverse('favorite-product-list', kwargs={'Customer_id': self.customer.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_remove_favorite_product(self):
        favorite_product = FavoriteProduct.objects.create(customer=self.customer, product_id=self.product)
        url = reverse('favorite-product-detail', kwargs={'customer_id': self.customer.id, 'product_id': self.product.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_favorite_product_detail(self):
        favorite_product = FavoriteProduct.objects.create(customer=self.customer, product_id=self.product)
        url = reverse('favorite-product-detail', kwargs={'customer_id': self.customer.id, 'product_id': self.product.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_id'], self.product.id)

class ProductImportTests(APITestCase):

    def test_import_products(self):
        url = reverse('import-products')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('imported', response.data)
        self.assertIn('skipped', response.data)
    
    def test_import_products_service_unavailable(self):
        # Simulate an external service failure or make it unavailable
        url = reverse('import-products')
        with self.assertRaises(requests.exceptions.RequestException):
            response = self.client.post(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
