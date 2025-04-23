from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import requests

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_register = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': 'E-mail inválido'})
    
    def __str__(self):
        return f"{self.name} ({self.email})"

class FavoriteProduct(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favoritos')
    product_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    review = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    date_addition = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('customer', 'product_id')
    
    @classmethod
    def validar_product(cls, product_id):
        try:
            response = requests.get(f'http://challenge-api.luizalabs.com/api/product/{product_id}')
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def clean(self):
        product_data = self.validar_product(self.product_id)
        if not product_data:
            raise ValidationError('product inválido ou não encontrado na API externa')
        
        # Preenche os dados do produto com base no retorno da api da LuizaLabs
        self.title = product_data.get('titulo', '')
        self.image = product_data.get('imagem', '')
        self.price = product_data.get('preco', 0)
        self.review = product_data.get('review')
    
    def __str__(self):
        return f"{self.title} (R$ {self.price})"