from django.shortcuts import render

from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Manufacturer, Product
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Константа, чтобы не хардкодить цифры
ITEMS_PER_PAGE = 1

class ManufacturerProductsView(View):
    def get(self, request, manufacturer_id):
        # --- ШАГ 1: Находим производителя ---
        # Если производитель не найден, Django сам вернёт 404.
        manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)

        # --- ШАГ 2: Берём все продукты производителя ---
        # Через related_name='products' (мы его задали в модели)
        all_products = manufacturer.products.all().order_by('name')  # сортировка для порядка

        # --- ШАГ 3: Реализуем пагинацию ---
        # Получаем номер страницы из GET-параметра (по умолчанию 1)
        page_number = int(request.GET.get('page', 1))

        # Вычисляем, с какого и по какой индекс брать товары
        start_index = (page_number - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE

        # Вытаскиваем нужные товары для текущей страницы
        # (Это называется "срез" QuerySet, он ленивый и делает только один запрос к БД)
        products_on_page = all_products[start_index:end_index]

        # --- ШАГ 4: Вычисляем общее количество страниц ---
        # count() делает быстрый SELECT COUNT(*) без загрузки всех объектов
        total_products = all_products.count()
        total_pages = (total_products + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  # округление вверх

        # --- ШАГ 5: Формируем ответ (пока простой, без шаблонов) ---
        html = f"""
        <h1>Товары производителя: {manufacturer.name}</h1>
        <ul>
        """

        for product in products_on_page:
            html += f"<li>{product.name} — {product.price} ₽ (в наличии: {product.stock_quantity})</li>"

        # Если на странице нет товаров — выводим сообщение
        if not products_on_page:
            html += "<li><em>Нет товаров на этой странице</em></li>"

        html += """
        </ul>
        <p>
        """

        # --- ШАГ 6: Строим навигацию по страницам ---
        if page_number > 1:
            prev_page = page_number - 1
            html += f'<a href="?page={prev_page}">← Предыдущая</a> | '
        else:
            html += '← Предыдущая | '

        html += f"Страница {page_number} из {total_pages}"

        if page_number < total_pages:
            next_page = page_number + 1
            html += f' | <a href="?page={next_page}">Следующая →</a>'
        else:
            html += ' | Следующая →'

        html += f"""
        </p>
        <p><a href="/manufacturers/1/products/">На первую страницу</a></p>
        """

        return HttpResponse(html)
    
    
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProductAvailabilityView(View):
    pass    

    def dispatch(self, request, *args, **kwargs):
        # 1. Проверяем метод запроса
        if request.method != 'POST':
            return JsonResponse({'error': 'Метод не разрешен.'}, status=405)
        
        # 2. Получаем SKU из URL
        sku = kwargs.get('sku')
        
        # 3. Ищем продукт по SKU (если нет — 404)
        try:
            self.product = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Продукт не найден.'}, status=404)
        
        # 4. Передаём управление дальше (в post())
        return super().dispatch(request, *args, **kwargs)    


    def post(self, request, sku):
        # 1. Получаем новый статус
        new_status = request.POST.get('status')
        
        # 2. Проверяем, что статус передан
        if new_status is None:
            return JsonResponse({'error': 'Поле "status" обязательно.'}, status=400)
        
        # 3. Проверяем, что статус — "true" или "false"
        if new_status == 'true':
            self.product.is_available = True
        elif new_status == 'false':
            self.product.is_available = False
        else:
            return JsonResponse({'error': 'Статус должен быть "true" или "false".'}, status=400)
        
        # 4. Сохраняем изменения
        self.product.save()
        
        # 5. Возвращаем успешный ответ
        return JsonResponse({
            'message': 'Статус обновлен.',
            'is_available': self.product.is_available
        })