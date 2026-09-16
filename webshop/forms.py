from django import forms
from decimal import Decimal


class ContactForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=100, help_text="Пожалуйста, введите ваше полное имя.")
    email = forms.EmailField(label="Ваш Email", help_text="Мы свяжемся с вами по этому адресу.")
    message = forms.CharField(label="Ваше сообщение", widget=forms.Textarea, help_text="Введите ваше сообщение здесь.")
    
    # Можно добавить метод clean_<field_name> для валидации конкретного поля
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Сообщение должно быть не менее 10 символов.")
        return message

class FeedbackForm(forms.Form):
    RATING_CHOICES = [
        ('1', '1 - Ужасно'),
        ('2', '2 - Плохо'),
        ('3', '3 - Средне'),
        ('4', '4 - Хорошо'),
        ('5', '5 - Отлично'),
    ]
    rating = forms.ChoiceField(label="Ваша оценка", choices=RATING_CHOICES, widget=forms.RadioSelect)
    comment = forms.CharField(label="Комментарий (необязательно)", required=False, widget=forms.Textarea)
    email = forms.EmailField(label="Ваш Email (необязательно)", required=False)

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        comment = cleaned_data.get('comment')

        if rating and int(rating) < 3 and not comment:
            self.add_error('comment', "Если оценка ниже 3, пожалуйста, оставьте комментарий.")
        return cleaned_data
    
class NewsletterSignupForm(forms.Form):
    email = forms.EmailField(
        label="Ваш Email",
        help_text="Введите Email для подписки на рассылку."
    )    
    
class ShippingCalculatorForm(forms.Form):
    weight = forms.DecimalField(
        label="Вес товара (кг)",
        min_value=0.1,
        max_digits=5,
        decimal_places=2,
        help_text="Введите вес товара в килограммах (например, 1.5)."
    )
    distance = forms.IntegerField(
        label="Расстояние доставки (км)",
        min_value=1,
        help_text="Введите расстояние в километрах."
    )    
class ProductSearchForm(forms.Form):
    query = forms.CharField(
        label="Название товара",
        max_length=200,
        required=False,
        help_text="Введите часть названия товара."
    )
    max_price = forms.DecimalField(
        label="Максимальная цена",
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0.01'),
        help_text="Найти товары дешевле или равные указанной цене."
    )    
    
class AskQuestionForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=100)
    email = forms.EmailField(label="Ваш Email")
    question = forms.CharField(label="Ваш вопрос", widget=forms.Textarea)   
    
class RectangleAreaForm(forms.Form):
    length = forms.DecimalField(label="Длина (м)", min_value=Decimal('0.1'))
    width = forms.DecimalField(label="Ширина (м)", min_value=Decimal('0.1'))     
    width = forms.DecimalField(label="Ширина (м)", min_value=Decimal('0.1')) 
    
class UserRegistrationForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", max_length=150)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают.")

        return cleaned_data     
    
class CustomProductOrderForm(forms.Form):
    COLOR_CHOICES = [
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('green', 'Зеленый'),
        ('black', 'Черный'),
        ('white', 'Белый'),
    ]

    product_name = forms.CharField(label="Название продукта", max_length=255)
    desired_color = forms.ChoiceField(label="Желаемый цвет", choices=COLOR_CHOICES)
    quantity = forms.IntegerField(label="Количество", min_value=1)       