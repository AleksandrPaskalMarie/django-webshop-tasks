from django.shortcuts import render
import datetime
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Manufacturer, Product
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView  # ← Добавь RedirectView
from django.urls import reverse
from django.views.generic import DetailView
from django.db.models.functions import Abs
from django.db.models import F
from django.views.generic import ListView
from django.db.models import Count, Q
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import ContactForm
from .forms import FeedbackForm
from .forms import NewsletterSignupForm

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



class RedirectToHomeView(RedirectView):
    pattern_name = 'home_page'
    permanent = False
    

class OldProductURLRedirectView(RedirectView):
    pattern_name = 'product_detail_with_related'  # Новый URL
    permanent = True                              # 301 — навсегда

    def get_redirect_url(self, *args, **kwargs):
        # Забираем старый SKU из URL
        old_sku = kwargs.get('old_sku')
        # Генерируем новый URL, подставляя этот SKU в pattern_name
        return reverse(self.pattern_name, kwargs={'product_sku': old_sku})   
    
class LegacySearchRedirectView(RedirectView):
    pattern_name = 'product_search'   # Новый адрес поиска
    query_string = True               # Передаём все GET-параметры
    permanent = False                 # Временный редирект (302) 
        

def product_search(request):
    q = request.GET.get('q', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    return HttpResponse(f"Поиск: q={q}, min={min_price}, max={max_price}")   

class ManufacturerLookupRedirectView(RedirectView):
    permanent = False # Временное перенаправление

    def get_redirect_url(self, *args, **kwargs):
        manufacturer_name = self.request.GET.get('name', '').strip()
        
        if manufacturer_name:
            # Пытаемся найти производителя по имени (регистронезависимо)
            manufacturer = Manufacturer.objects.filter(name__iexact=manufacturer_name).first()
            
            if manufacturer:
                # Если найден, перенаправляем на его панель
                return reverse('manufacturer_dashboard', kwargs={'manufacturer_id': manufacturer.id})
        
        # Если имя не указано или производитель не найден, перенаправляем на общий список
        return reverse('manufacturer_list')

def manufacturer_dashboard(request, manufacturer_id):
    manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
    return HttpResponse(f"Дашборд производителя: {manufacturer.name}")

class ProductUnavailableView(TemplateView):
    template_name = 'webshop/product_unavailable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем SKU из GET-параметра, если он был передан при перенаправлении
        context['product_sku'] = self.request.GET.get('sku')
        return context

class ProductAvailabilityRedirectView(RedirectView):
    permanent = False # Временное перенаправление

    def get_redirect_url(self, *args, **kwargs):
        product_sku = kwargs.get('product_sku')
        
        if product_sku:
            product = Product.objects.filter(sku=product_sku).first()
            
            if product and product.is_available and product.stock_quantity > 0:
                # Продукт найден и доступен, перенаправляем на его детальную страницу
                return reverse('product_detail_with_related', kwargs={'product_sku': product_sku})
        
        # Продукт не найден, или недоступен, или нет в наличии
        # Перенаправляем на страницу "недоступно", передавая SKU как GET-параметр
        return f"{reverse('product_unavailable')}?sku={product_sku}"

class ManufacturerDetailView(DetailView):
    model = Manufacturer
    template_name = 'webshop/manufacturer_detail.html'
    context_object_name = 'manufacturer'  # чтобы в шаблоне было {{ manufacturer }}, а не {{ object }}
    
class ProductDetailBySkuView(DetailView):
    model = Product
    template_name = 'webshop/product_detail.html'
    context_object_name = 'product'
    
    # Поиск по SKU, а не по pk
    slug_field = 'sku'                # Поле в модели, по которому ищем
    slug_url_kwarg = 'product_sku'    # Имя параметра в URL    
    
class ManufacturerProductsDetailView(DetailView):
    model = Manufacturer
    template_name = 'webshop/manufacturer_detail_with_products.html'
    context_object_name = 'manufacturer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object — это уже найденный производитель
        context['products'] = self.object.products.all()
        return context  
    
class ProductDetailWithViewCount(DetailView):
    model = Product
    template_name = 'webshop/product_detail.html'
    context_object_name = 'product'
    
    # Поиск по SKU
    slug_field = 'sku'
    slug_url_kwarg = 'product_sku'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем объект продукта (уже найден DetailView)
        product = self.object
        
        # Получаем словарь просмотров из сессии (или создаём пустой)
        product_views = self.request.session.get('product_views', {})
        
        # Получаем текущий счётчик для этого SKU (по умолчанию 0)
        current_count = product_views.get(product.sku, 0)
        
        # Увеличиваем счётчик
        current_count += 1
        
        # Сохраняем обратно в словарь
        product_views[product.sku] = current_count
        
        # Сохраняем словарь в сессию
        self.request.session['product_views'] = product_views
        
        # Помечаем сессию как изменённую (чтобы Django её сохранил)
        self.request.session.modified = True
        
        # Добавляем счётчик в контекст
        context['view_count_in_session'] = current_count
        
        return context
    
class ProductDetailWithSimilarPriceView(DetailView):
    model = Product
    template_name = 'webshop/product_detail.html'
    context_object_name = 'product'

    slug_field = 'sku'
    slug_url_kwarg = 'product_sku'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Берём все доступные товары того же производителя, кроме текущего
        similar = Product.objects.filter(
            manufacturer=product.manufacturer,
            is_available=True
        ).exclude(id=product.id)

        # Аннотируем разницей цен и сортируем по ней
        similar = similar.annotate(
            price_diff=Abs(F('price') - product.price)
        ).order_by('price_diff')[:3]

        context['similar_price_products'] = similar
        return context    
    
    
class ManufacturerListView(ListView):
    model = Manufacturer
    template_name = 'webshop/manufacturer_list.html'
    context_object_name = 'manufacturer_list'
    paginate_by = 5  # по 5 производителей на страницу  
    
class ProductFilteredListView(ListView):
    model = Product
    template_name = 'webshop/product_list_filtered.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        # Базовый QuerySet: только доступные продукты
        queryset = Product.objects.filter(is_available=True)
        
        # Получаем GET-параметр
        manufacturer_name = self.request.GET.get('manufacturer_name', '').strip()
        
        # Если параметр не пуст — фильтруем по имени производителя
        if manufacturer_name:
            queryset = queryset.filter(manufacturer__name__icontains=manufacturer_name)
        
        # Сортируем по имени продукта
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём текущее значение фильтра в шаблон
        context['current_manufacturer_name'] = self.request.GET.get('manufacturer_name', '').strip()
        return context    
    
from django.views.generic import ListView
from .models import Product

class ProductSortableListView(ListView):
    model = Product
    template_name = 'webshop/product_list_sortable.html'
    context_object_name = 'product_list'

    # Допустимые поля для сортировки
    ALLOWED_SORT_FIELDS = [
        'name', '-name',
        'price', '-price',
        'stock_quantity', '-stock_quantity',
    ]

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Получаем GET-параметр
        sort_by = self.request.GET.get('sort_by', '').strip()
        
        # Если параметр допустим — сортируем по нему
        if sort_by in self.ALLOWED_SORT_FIELDS:
            queryset = queryset.order_by(sort_by)
        else:
            # Иначе — сортировка по умолчанию
            queryset = queryset.order_by('name')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём текущее значение сортировки в шаблон
        context['current_sort_by'] = self.request.GET.get('sort_by', '').strip()
        return context    
    
class ManufacturerStatsListView(ListView):
    model = Manufacturer
    template_name = 'webshop/manufacturer_list_with_stats.html'
    context_object_name = 'manufacturer_list'

    def get_queryset(self):
        return Manufacturer.objects.annotate(
            available_count=Count(
                'products',
                filter=Q(products__is_available=True)
            ),
            unavailable_count=Count(
                'products',
                filter=Q(products__is_available=False)
            )
        )    
        
class ProductAdvancedFilterListView(ListView):
    model = Product
    template_name = 'webshop/product_list_advanced_filter.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        queryset = Product.objects.all()

        # Фильтр по наличию
        available = self.request.GET.get('available', '').strip()
        if available == 'true':
            queryset = queryset.filter(is_available=True)
        elif available == 'false':
            queryset = queryset.filter(is_available=False)

        # Фильтр по минимальной цене
        min_price = self.request.GET.get('min_price', '').strip()
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass  # если ввели не число — игнорируем

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_available'] = self.request.GET.get('available', '').strip()
        context['current_min_price'] = self.request.GET.get('min_price', '').strip()
        return context
    
class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'webshop/contact_form.html'
    success_url = reverse_lazy('contact_success')

    def form_valid(self, form):
        # Имитация отправки email или сохранения
        print(f"[📩] Новое сообщение от {form.cleaned_data['name']}")
        print(f"[📧] Email: {form.cleaned_data['email']}")
        print(f"[💬] Сообщение: {form.cleaned_data['message']}")
        return super().form_valid(form)  
    
class FeedbackFormView(FormView):
    form_class = FeedbackForm
    template_name = 'webshop/feedback_form.html'
    success_url = reverse_lazy('feedback_thank_you')

    def form_valid(self, form):
        # Сохраняем форму в self, чтобы get_success_url() мог её использовать
        self.form = form
        
        # Логируем данные
        print(f"[📝] Новая оценка: {form.cleaned_data['rating']}")
        print(f"[💬] Комментарий: {form.cleaned_data.get('comment', 'нет')}")
        print(f"[📧] Email: {form.cleaned_data.get('email', 'нет')}")
        
        return super().form_valid(form)

    def get_success_url(self):
        rating = self.form.cleaned_data.get('rating', '')
        base_url = reverse_lazy('feedback_thank_you')
        return f"{base_url}?rating={rating}"


class FeedbackThankYouView(TemplateView):
    template_name = 'webshop/feedback_thank_you.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rating'] = self.request.GET.get('rating', '')
        return context              
    
class NewsletterSignupView(FormView):
    form_class = NewsletterSignupForm
    template_name = 'webshop/newsletter_signup.html'
    success_url = reverse_lazy('newsletter_success')

    def form_valid(self, form):
        # Имитация сохранения в БД или отправки письма
        email = form.cleaned_data['email']
        print(f"[📧] Новая подписка: {email}")
        return super().form_valid(form)
    