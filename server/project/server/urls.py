from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import UserViewSet, ShopViewSet, FidelityProgramViewSet, CatalogueViewSet, ProductViewSet, \
    TransactionViewSet, CustomAuthToken

# Create a router and register viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'shops', ShopViewSet, basename="shop")
router.register(r'fidelityprograms', FidelityProgramViewSet, basename='fidelityprogram')
router.register(r'catalogue', CatalogueViewSet, basename='catalogue')
router.register(r'product', ProductViewSet, basename='product')
router.register(r'transactions', TransactionViewSet, basename='transaction')

# The API URLs are determined automatically by the router.
urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api-token-auth/', CustomAuthToken.as_view()),
    path(r'', include(router.urls)),
]