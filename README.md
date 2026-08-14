
---

# 🧠 Django Training Project

Этот проект содержит обучающие модели и данные для решения практических задач по Django ORM: `F`, `Q`, `annotate`, `Window`, `ExpressionWrapper`, `Rank`, `Concat` и другим.

## 🚀 Установка и запуск проекта

### 🔁 1. Клонирование репозитория

```bash
git clone https://github.com/username/training_project.git
cd training_project
```

### 🧱 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

(Для Windows: `venv\Scripts\activate`)

### 📦 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## 🗃️ Работа с базой данных

### 📂 4. Восстановление базы данных

Мы используем **PostgreSQL**. Убедитесь, что PostgreSQL установлен и запущен.

Восстанови базу данных из дампа (внутри проекта есть файл `dump.sql`):

```bash
createdb training_db
psql -U <ваш_пользователь_postgres> -d training_db -f dump.sql
```

📝 *Не забудь заменить `<ваш_пользователь_postgres>` на своё имя пользователя PostgreSQL.*

---

## ⚙️ 5. Настройки подключения к БД

Открой `training_project/settings.py` и укажи свои параметры подключения к PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'training_db',
        'USER': 'ваш_пользователь',
        'PASSWORD': 'ваш_пароль',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## ▶️ 6. Запуск проекта

```bash
python manage.py runserver
```

---

## ✍️ Цель проекта

Проект разработан для практики и тестирования знаний в следующих темах:

- Работа с ORM: `filter`, `get`, `update`, `create`, `delete`
- Агрегации: `Count`, `Avg`, `Sum`
- Аннотации и выражения: `annotate`, `F`, `Q`, `ExpressionWrapper`
- Продвинутые конструкции: `Case`, `When`, `Window`, `DenseRank`, `Rank`
- Работа с датами и временем
- Подготовка интерактивных заданий для Stepik или обучающих платформ

---

## 💬 Обратная связь

Если у тебя есть предложения по улучшению или ты хочешь добавить новые задачи — **открой issue или отправь pull request!**

---

