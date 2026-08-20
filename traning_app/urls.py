from django.urls import path
from . import views

urlpatterns = [
    path('category/<str:category_name>/', views.products_by_category, name='products_by_category'),
    path('top-products/', views.top_products, name='top_products'),
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/products/<int:product_id>/update-price/', views.update_product_price, name='update_product_price'),
]