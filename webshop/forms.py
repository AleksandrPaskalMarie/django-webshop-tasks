from django import forms

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