from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def products_by_category(request, category_name):
    # Ищем категорию по имени, если нет — 404
    category = get_object_or_404(Category, name=category_name)
    
    # Получаем все продукты, связанные с этой категорией
    products = category.products.all()
    
    return render(request, 'training_app/products_by_category.html', {
        'category': category,
        'products': products
    })

def top_products(request):
    # Получаем параметры из GET-запроса
    min_rating = request.GET.get('min_rating')
    min_discount = request.GET.get('min_discount')

    # Преобразуем в числа, если параметры переданы, иначе None
    try:
        min_rating = float(min_rating) if min_rating else 0.0
    except ValueError:
        min_rating = 0.0

    try:
        min_discount = float(min_discount) if min_discount else 0.0
    except ValueError:
        min_discount = 0.0

    # Фильтруем продукты
    products = Product.objects.filter(
        rating__gte=min_rating,
        discount__gte=min_discount
    ).order_by('-rating')

    return render(request, 'top_products.html', {
        'products': products,
        'min_rating': min_rating,
        'min_discount': min_discount
    }) 


def api_product_detail(request, product_id):
    # Пытаемся найти продукт, если нет — 404
    product = get_object_or_404(Product, id=product_id)
    
    # Собираем данные в словарь
    data = {
        'id': product.id,
        'name': product.name,
        'price': str(product.price),  # Decimal → str для JSON
        'rating': product.rating,
        'discount': product.discount,
        'category': product.category.name,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }
    
    return JsonResponse(data)       


@csrf_exempt  # временно отключаем CSRF для тестирования через curl
def update_product_price(request, product_id):
    # Проверяем, что метод POST
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Method not allowed',
            'message': 'Only POST requests are allowed.'
        }, status=405)
    
    # Ищем продукт
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем новую цену
    # request.POST — для form-data, request.body — для JSON
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            new_price = data.get('new_price')
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON.'
            }, status=400)
    else:
        new_price = request.POST.get('new_price')
    
    # Проверяем, что цена передана
    if new_price is None:
        return JsonResponse({
            'error': 'Missing field',
            'message': 'Field "new_price" is required.'
        }, status=400)
    
    # Пробуем преобразовать в число
    try:
        new_price = float(new_price)
    except (ValueError, TypeError):
        return JsonResponse({
            'error': 'Invalid price',
            'message': 'Price must be a number.'
        }, status=400)
    
    # Обновляем цену
    product.price = new_price
    product.save()
    
    # Возвращаем подтверждение
    return JsonResponse({
        'status': 'success',
        'message': f'Price updated for product "{product.name}"',
        'product_id': product.id,
        'new_price': str(product.price)
    }, status=200)