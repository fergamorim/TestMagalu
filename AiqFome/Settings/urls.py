from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.generators import OpenAPISchemaGenerator

class PublicSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        if public:
            for path in list(schema.paths.keys()):
                if path.startswith('/api/'):
                    del schema.paths[path]
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="API de Produtos Favoritos",
        default_version='v1',
        description="Documentação pública da API",
        terms_of_service="https://www.suaapi.com/terms/",
        contact=openapi.Contact(email="contato@suaapi.com"),
        license=openapi.License(name="BSD License"),
    ),
    generator_class=PublicSchemaGenerator,
    public=True,  # Define como True para acesso público
    permission_classes=(permissions.AllowAny,),  # Permite acesso sem autenticação
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Customer_api.urls')),
    # URLs da documentação pública
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]