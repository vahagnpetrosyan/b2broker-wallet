from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)



urlpatterns = [
    path('api/', include('wallets.urls')),  # Include endpoints from the wallets app
    # OpenAPI schema:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI:
    path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc:
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
