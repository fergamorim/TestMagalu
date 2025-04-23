from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customer, FavoriteProduct
import json

User = get_user_model()

class TestSetup(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        response = self.client.post(
            self.token_url,
            self.user_data,
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.Customer_data = {
            'nome': 'Cliente Teste',
            'email': 'Cliente@teste.com'
        }
        self.Customer = Customer.objects.create(**self.Customer_data)
        
        # URLs para os endpoints
        self.Customers_url = reverse('Customer-list-create')
        self.Customer_detail_url = reverse('Customer-detail', kwargs={'id': self.Customer.id})
        
        # Dados de produto favorito *mock*
        self.produto_data = {
            'product_id': 'prod123',
            'title': 'Produto Teste',
            'image': 'http://luzizLabs.com/produto.jpg',
            'price': 99.99,
            'review': 4.5
        }
        self.produto_favorito = FavoriteProduct.objects.create(
            Customer=self.Customer,
            **self.produto_data
        )
        self.favoritos_url = reverse('favorite-list', kwargs={'Customer_id': self.Customer.id})
        self.favorito_detail_url = reverse(
            'favorite-detail',
            kwargs={
                'Customer_id': self.Customer.id,
                'product_id': self.produto_favorito.id
            }
        )
        
        # Configurar mock para API externa
        self.patcher = None
        
    def tearDown(self):
        if self.patcher:
            self.patcher.stop()
        super().tearDown()

class AuthTests(TestSetup):
    def test_registro_usuario(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('access' in response.data)
    
    def test_login_usuario(self):
        response = self.client.post(self.token_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
    
    def test_acesso_nao_autorizado(self):
        client = APIClient()  # Client sem autenticação
        response = client.get(self.Customers_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class CustomerModelTests(TestSetup):
    def test_criacao_Customer(self):
        Customer = Customer.objects.create(
            nome='Novo Cliente',
            email='novo@Cliente.com'
        )
        self.assertEqual(str(Customer), 'Novo Cliente (novo@Cliente.com)')
        self.assertTrue(Customer.data_cadastro is not None)
    
    def test_email_unico(self):
        with self.assertRaises(Exception):
            Customer.objects.create(
                nome='Cliente Duplicado',
                email='Customer@teste.com'
            )
    
    def test_validacao_email(self):
        Customer = Customer(
            nome='Cliente Inválido',
            email='email-invalido'
        )
        with self.assertRaises(ValidationError):
            Customer.full_clean()

class FavoriteProductModelTests(TestSetup):
    def test_criacao_produto_favorito(self):
        produto = FavoriteProduct.objects.create(
            Customer=self.Customer,
            product_id='prod456',
            titulo='Outro Produto',
            imagem='http://teste.com/outro.jpg',
            preco=50.00
        )
        self.assertEqual(str(produto), 'Outro Produto (R$ 50.00)')
        self.assertTrue(produto.data_adicao is not None)
    
    def test_produto_unico_por_Customer(self):
        with self.assertRaises(Exception):
            FavoriteProduct.objects.create(
                Customer=self.Customer,
                product_id='prod123',  # Já existe para este cliente
                titulo='Produto Duplicado',
                imagem='http://teste.com/duplicado.jpg',
                preco=10.00
            )

class CustomerViewTests(TestSetup):
    def test_listar_Customers(self):
        response = self.client.get(self.Customers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], self.Customer_data['nome'])
    
    def test_criar_Customer(self):
        data = {
            'nome': 'Novo Customer',
            'email': 'novo@Customer.com'
        }
        response = self.client.post(self.Customers_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
    
    def test_email_duplicado(self):
        response = self.client.post(
            self.Customers_url,
            self.Customer_data,  # Email duplicado
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('email' in response.data)
    
    def test_detalhes_Customer(self):
        response = self.client.get(self.Customer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.Customer_data['nome'])
    
    def test_atualizar_Customer(self):
        data = {'nome': 'Cliente Atualizado'}
        response = self.client.patch(self.Customer_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.Customer.refresh_from_db()
        self.assertEqual(self.Customer.nome, 'Cliente Atualizado')
    
    def test_deletar_Customer(self):
        response = self.client.delete(self.Customer_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

class FavoriteProductViewTests(TestSetup):
    def setUp(self):
        super().setUp()
        # Mock para a API externa de validação de produtos
        from unittest.mock import patch
        self.patcher = patch('requests.get')
        self.mock_get = self.patcher.start()
        
        # Configurar o mock para retornar dados válidos
        self.mock_get.return_value.status_code = 200
        self.mock_get.return_value.json.return_value = {
            'title': 'Produto Validado',
            'image': 'http://luizalabs.com/validado.jpg',
            'price': 150.00,
            'review': 4.8
        }
    
    def test_listar_favoritos(self):
        response = self.client.get(self.favoritos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.produto_data['title'])
    
    def test_criar_favorito(self):
        data = {'product_id': 'prod789'}
        response = self.client.post(self.favoritos_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteProduct.objects.count(), 2)
        
        # Verifica se os dados foram preenchidos pela API externa
        produto = FavoriteProduct.objects.get(product_id='prod789')
        self.assertEqual(produto.titulo, 'Produto Validado')
    
    def test_produto_duplicado(self):
        data = {'product_id': 'prod123'}  # Já existe
        response = self.client.post(self.favoritos_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('product_id' in response.data)
    
    def test_produto_invalido(self):
        # Configurar mock para retornar produto inválido
        self.mock_get.return_value.status_code = 404
        
        data = {'product_id': 'prod-invalido'}
        response = self.client.post(self.favoritos_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data)
    
    def test_detalhes_favorito(self):
        response = self.client.get(self.favorito_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.produto_data['title'])
    
    def test_atualizar_favorito(self):
        data = {'review': 5.0}
        response = self.client.patch(self.favorito_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.produto_favorito.refresh_from_db()
        self.assertEqual(self.produto_favorito.review, 5.0)
    
    def test_deletar_favorito(self):
        response = self.client.delete(self.favorito_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteProduct.objects.count(), 0)