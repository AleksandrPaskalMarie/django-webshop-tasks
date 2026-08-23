from django.urls import path
from . import views

urlpatterns = [
    # ... другие маршруты
    path('manufacturers/<int:manufacturer_id>/products/', views.ManufacturerProductsView.as_view(), name='manufacturer_products'),
    path('api/products/<str:sku>/availability/', views.UpdateProductAvailabilityView.as_view(), name='update_availability'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('', views.WelcomeHomeView.as_view(), name='home'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('products/<str:product_sku>/detail/', views.ProductDetailWithRelatedView.as_view(), name='product_detail_with_related'),
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
]
