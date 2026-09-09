from django.shortcuts import render
import datetime
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Manufacturer, Product
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

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
class AboutUsView(TemplateView):
    template_name = 'webshop/about.html'
    
class WelcomeHomeView(TemplateView):
    template_name = 'webshop/home.html'

    def get_context_data(self, **kwargs):
        # 1. Получаем базовый контекст от родителя
        context = super().get_context_data(**kwargs)

        # 2. Добавляем текущий год
        context['current_year'] = datetime.datetime.now().year

        # 3. Получаем имя из GET-параметра, если есть
        name = self.request.GET.get('name')
        if name:
            context['username'] = name
        else:
            context['username'] = 'Гость'

        return context
    
class FAQView(TemplateView):
    template_name = 'webshop/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        faq_items = [
            {'question': 'Что вы продаете?', 'answer': 'Электроника, книги, одежда.'},
            {'question': 'Как сделать заказ?', 'answer': 'Добавьте товары в корзину и оформите заказ.'},
            {'question': 'Есть ли доставка?', 'answer': 'Да, доставляем по всей стране.'},
        ]

        context['faq_items'] = faq_items
        return context
   
class ProductDetailWithRelatedView(TemplateView):
    template_name = 'webshop/product_detail_with_related.html'
    
    def get_context_data(self, **kwargs):
        # 1. ВЫЗЫВАЕМ РОДИТЕЛЯ (ОБЯЗАТЕЛЬНО!)
        context = super().get_context_data(**kwargs)
        
        # 2. ДОСТАЁМ SKU ИЗ URL (он придёт в kwargs)
        product_sku = kwargs.get('product_sku')
        
        # 3. ИЩЕМ ПРОДУКТ ИЛИ КИДАЕМ 404
        product = get_object_or_404(Product, sku=product_sku)
        
        # 4. ИЩЕМ СВЯЗАННЫЕ ТОВАРЫ
        #    Идём от производителя (product.manufacturer),
        #    берём все его товары (products),
        #    исключаем текущий (exclude(id=product.id))
        related_products = product.manufacturer.products.exclude(id=product.id)
        
        # 5. КЛАДЁМ В КОНТЕКСТ
        context['product'] = product
        context['related_products'] = related_products
        
        # 6. ВОЗВРАЩАЕМ
        return context

from django.db.models import Count, Q

class ManufacturerListView(TemplateView):
    template_name = 'webshop/manufacturer_list.html'

    def get_context_data(self, **kwargs):
        # 1. БАЗОВЫЙ КОНТЕКСТ (ОБЯЗАТЕЛЬНО)
        context = super().get_context_data(**kwargs)

        # 2. ПОЛУЧАЕМ GET-ПАРАМЕТР
        country_filter = self.request.GET.get('country', '').strip()

        # 3. СТРОИМ ЗАПРОС
        #    - Аннотируем каждый объект Manufacturer полем active_product_count
        #    - Считаем только продукты с is_available=True
        manufacturers = Manufacturer.objects.annotate(
            active_product_count=Count(
                'products',  # related_name из модели Product
                filter=Q(products__is_available=True)  # Только активные!
            )
        )

        # 4. ПРИМЕНЯЕМ ФИЛЬТР ПО СТРАНЕ (ЕСЛИ ЗАДАН)
        if country_filter:
            manufacturers = manufacturers.filter(
                country__icontains=country_filter
            )

        # 5. КЛАДЁМ В КОНТЕКСТ
        context['manufacturers'] = manufacturers
        context['current_country'] = country_filter

        return context


from django.views.generic import RedirectView

class RedirectToHomeView(RedirectView):
    pattern_name = 'home_page'
    permanent = False
    
from django.urls import reverse

class OldProductURLRedirectView(RedirectView):
    pattern_name = 'product_detail_with_related'  # Новый URL
    permanent = True                              # 301 — навсегда

    def get_redirect_url(self, *args, **kwargs):
        # Забираем старый SKU из URL
        old_sku = kwargs.get('old_sku')
        # Генерируем новый URL, подставляя этот SKU в pattern_name
        return reverse(self.pattern_name, kwargs={'product_sku': old_sku})    