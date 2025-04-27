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

class Product(models.Model):
    api_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=100)
    image_url = models.URLField()
    rating_rate = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    rating_count = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
    
    def __str__(self):
        return self.title

class FavoriteProduct(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favoritos')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='produtos')
    date_addition = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('customer', 'product_id')
    
    @classmethod
    def validar_product(cls, product_id):
        try:
            response = requests.get(f'https://fakestoreapi.com/products/{product_id}')
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def clean(self):
        # Verifica se o produto associado ao favorite é válido
        if not self.product_id:
            raise ValidationError('Produto não pode ser nulo.')

        product_data = self.validar_product(self.product_id.api_id)  # Usar o api_id para validar
        if not product_data:
            raise ValidationError('Produto inválido ou não encontrado na API externa')
    
    def __str__(self):
        return f"Favorito: {self.product_id.title} (R$ {self.product_id.price})"
