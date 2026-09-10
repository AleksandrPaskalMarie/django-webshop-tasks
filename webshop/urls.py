from django.urls import path
from . import views
from .views import RedirectToHomeView
from .views import OldProductURLRedirectView
from .views import LegacySearchRedirectView

urlpatterns = [
    # --- ПОИСК ---
    path('products/search/', views.product_search, name='product_search'),

    # --- ПРОИЗВОДИТЕЛИ ---
    path('manufacturers/<int:manufacturer_id>/products/', views.ManufacturerProductsView.as_view(), name='manufacturer_products'),
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path('manufacturers/<int:manufacturer_id>/dashboard/', views.manufacturer_dashboard, name='manufacturer_dashboard'),

    # --- API ---
    path('api/products/<str:sku>/availability/', views.UpdateProductAvailabilityView.as_view(), name='update_availability'),

    # --- СТАТИЧЕСКИЕ СТРАНИЦЫ ---
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('', views.WelcomeHomeView.as_view(), name='home_page'),
    path('faq/', views.FAQView.as_view(), name='faq'),

    # --- ТОВАРЫ ---
    path('products/<str:product_sku>/detail/', views.ProductDetailWithRelatedView.as_view(), name='product_detail_with_related'),

    # --- РЕДИРЕКТЫ ---
    path('old-home/', RedirectToHomeView.as_view(), name='old_home_redirect'),
    path('old-products-url/<str:old_sku>/', OldProductURLRedirectView.as_view(), name='old_product_url_redirect'),
    path('legacy-search/', LegacySearchRedirectView.as_view(), name='legacy_search_redirect'),

    # --- УМНЫЙ РЕДИРЕКТ ПО ИМЕНИ ПРОИЗВОДИТЕЛЯ ---
    path('find-manufacturer/', views.ManufacturerLookupRedirectView.as_view(), name='find_manufacturer'),
    path('product-unavailable/', views.ProductUnavailableView.as_view(), name='product_unavailable'),
    path('product-status/<str:product_sku>/', views.ProductAvailabilityRedirectView.as_view(), name='product_availability_status'),
    path('manufacturers/<int:pk>/', views.ManufacturerDetailView.as_view(), name='manufacturer_detail'),
    path('products/<str:product_sku>/', views.ProductDetailBySkuView.as_view(), name='product_detail_by_sku'),
    path('manufacturers/<int:pk>/detail-products/', views.ManufacturerProductsDetailView.as_view(), name='manufacturer_products_detail'),
    path('products/counted/<str:product_sku>/', views.ProductDetailWithViewCount.as_view(), name='product_detail_with_count'),
]