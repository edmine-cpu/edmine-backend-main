def get_localized_field(obj, field_name, lang):
    """Get localized field value from an object based on language"""
    field_attr = f"{field_name}_{lang}"
    if hasattr(obj, field_attr):
        return getattr(obj, field_attr)
    
    # Fallback to Ukrainian if requested language is not available
    fallback_attr = f"{field_name}_uk"
    if hasattr(obj, fallback_attr):
        return getattr(obj, fallback_attr)
    
    return None


# Словари переводов для всех языков интерфейса
TRANSLATIONS = {
    'uk': {
        # Общие
        'site_title': 'FreelanceBirja',
        'site_description': 'Біржа послуг та виконавців',
        'home': 'На головну',
        'catalog': 'Каталог',
        'performers': 'Виконавці',
        'create_request': 'Створити заявку',
        'login': 'Увійти',
        'register': 'Реєстрація',
        'logout': 'Вийти',
        'search': 'Пошук',
        'reset_filters': 'Скинути фільтри',
        'apply_filters': 'Застосувати фільтри',
        'all_categories': 'Всі категорії',
        'all_cities': 'Всі міста та області',
        'select_city': 'Оберіть місто',
        'newest': 'Найновіші',
        'oldest': 'Найстаріші',
        'sort_by': 'Сортування',
        
        # Категорії та підкатегорії
        'category': 'Категорія',
        'subcategory': 'Підкатегорія',
        'select_category': 'Оберіть категорію',
        'select_subcategory': 'Оберіть підкатегорію',
        
        # Форми
        'name': 'Ім\'я',
        'email': 'Email',
        'password': 'Пароль',
        'city': 'Місто / регіон',
        'language': 'Мова',
        'phone': 'Телефон',
        'description': 'Опис',
        'title': 'Назва',
        'message': 'Повідомлення',
        'required_field': 'Обов\'язкове поле',
        
        # Заявки
        'bid_title': 'Назва заявки',
        'bid_description': 'Опис завдання',
        'create_bid': 'Створити заявку',
        'edit_bid': 'Редагувати заявку',
        'delete_bid': 'Видалити заявку',
        'respond_to_bid': 'Відгукнутися',
        'bid_created': 'Заявка створена',
        'bid_deleted': 'Заявка видалена',
        'files': 'Файли',
        'attach_files': 'Прикріпити файли',
        
        # Виконавці
        'performers_catalog': 'Каталог виконавців',
        'days_on_service': 'Днів на сервісі',
        'categories': 'Категорії',
        'subcategories': 'Підкатегорії',
        'contact_performer': 'Зв\'язатися',
        
        # Повідомлення
        'success': 'Успішно',
        'error': 'Помилка',
        'loading': 'Завантаження...',
        'no_results': 'Результатів не знайдено',
        'try_again': 'Спробуйте ще раз',
        
        # Аутентифікація
        'sign_in': 'Увійти',
        'sign_up': 'Зареєструватися',
        'forgot_password': 'Забули пароль?',
        'reset_password': 'Скинути пароль',
        'confirm_email': 'Підтвердити email',
        'verification_code': 'Код підтвердження',
        'resend_code': 'Повторно надіслати код',
        
        # Валідація
        'field_required': 'Поле обов\'язкове',
        'invalid_email': 'Невірний email',
        'password_too_short': 'Пароль занадто короткий',
        'passwords_not_match': 'Паролі не співпадають',
        'invalid_code': 'Невірний код',
        
        # Фільтри
        'filter_by_category': 'Фільтр за категорією',
        'filter_by_subcategory': 'Фільтр за підкатегорією',
        'filter_by_city': 'Фільтр за містом',
        'filter_by_date': 'Фільтр за датою',
        
        # Перевод
        'auto_translated': '(автоперекладено)',
        'translation_marker': '(перекладено)',
        'original_language': 'Оригінальна мова',
        'show_other_languages': 'Показати інші мови',
        'hide_other_languages': 'Приховати інші мови',
    },
    
    'en': {
        # General
        'site_title': 'FreelanceBirja',
        'site_description': 'Services and Performers Exchange',
        'home': 'Home',
        'catalog': 'Catalog',
        'performers': 'Performers',
        'create_request': 'Create Request',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'search': 'Search',
        'reset_filters': 'Reset Filters',
        'apply_filters': 'Apply Filters',
        'all_categories': 'All Categories',
        'all_cities': 'All Cities and Regions',
        'select_city': 'Select City',
        'newest': 'Newest',
        'oldest': 'Oldest',
        'sort_by': 'Sort By',
        
        # Categories and Subcategories
        'category': 'Category',
        'subcategory': 'Subcategory',
        'select_category': 'Select Category',
        'select_subcategory': 'Select Subcategory',
        
        # Forms
        'name': 'Name',
        'email': 'Email',
        'password': 'Password',
        'city': 'City / Region',
        'language': 'Language',
        'phone': 'Phone',
        'description': 'Description',
        'title': 'Title',
        'message': 'Message',
        'required_field': 'Required Field',
        
        # Bids
        'bid_title': 'Request Title',
        'bid_description': 'Task Description',
        'create_bid': 'Create Request',
        'edit_bid': 'Edit Request',
        'delete_bid': 'Delete Request',
        'respond_to_bid': 'Respond',
        'bid_created': 'Request Created',
        'bid_deleted': 'Request Deleted',
        'files': 'Files',
        'attach_files': 'Attach Files',
        
        # Performers
        'performers_catalog': 'Performers Catalog',
        'days_on_service': 'Days on Service',
        'categories': 'Categories',
        'subcategories': 'Subcategories',
        'contact_performer': 'Contact',
        
        # Messages
        'success': 'Success',
        'error': 'Error',
        'loading': 'Loading...',
        'no_results': 'No Results Found',
        'try_again': 'Try Again',
        
        # Authentication
        'sign_in': 'Sign In',
        'sign_up': 'Sign Up',
        'forgot_password': 'Forgot Password?',
        'reset_password': 'Reset Password',
        'confirm_email': 'Confirm Email',
        'verification_code': 'Verification Code',
        'resend_code': 'Resend Code',
        
        # Validation
        'field_required': 'Field is required',
        'invalid_email': 'Invalid email',
        'password_too_short': 'Password too short',
        'passwords_not_match': 'Passwords do not match',
        'invalid_code': 'Invalid code',
        
        # Filters
        'filter_by_category': 'Filter by Category',
        'filter_by_subcategory': 'Filter by Subcategory',
        'filter_by_city': 'Filter by City',
        'filter_by_date': 'Filter by Date',
        
        # Translation
        'auto_translated': '(auto-translated)',
        'translation_marker': '(translated)',
        'original_language': 'Original Language',
        'show_other_languages': 'Show Other Languages',
        'hide_other_languages': 'Hide Other Languages',
    },
    
    'pl': {
        # Ogólne
        'site_title': 'FreelanceBirja',
        'site_description': 'Giełda Usług i Wykonawców',
        'home': 'Strona Główna',
        'catalog': 'Katalog',
        'performers': 'Wykonawcy',
        'create_request': 'Utwórz Zlecenie',
        'login': 'Zaloguj',
        'register': 'Rejestracja',
        'logout': 'Wyloguj',
        'search': 'Szukaj',
        'reset_filters': 'Zresetuj Filtry',
        'apply_filters': 'Zastosuj Filtry',
        'all_categories': 'Wszystkie Kategorie',
        'all_cities': 'Wszystkie Miasta i Regiony',
        'select_city': 'Wybierz Miasto',
        'newest': 'Najnowsze',
        'oldest': 'Najstarsze',
        'sort_by': 'Sortuj według',
        
        # Kategorie i Podkategorie
        'category': 'Kategoria',
        'subcategory': 'Podkategoria',
        'select_category': 'Wybierz Kategorię',
        'select_subcategory': 'Wybierz Podkategorię',
        
        # Formularze
        'name': 'Imię',
        'email': 'Email',
        'password': 'Hasło',
        'city': 'Miasto / Region',
        'language': 'Język',
        'phone': 'Telefon',
        'description': 'Opis',
        'title': 'Tytuł',
        'message': 'Wiadomość',
        'required_field': 'Pole wymagane',
        
        # Zlecenia
        'bid_title': 'Tytuł Zlecenia',
        'bid_description': 'Opis Zadania',
        'create_bid': 'Utwórz Zlecenie',
        'edit_bid': 'Edytuj Zlecenie',
        'delete_bid': 'Usuń Zlecenie',
        'respond_to_bid': 'Odpowiedz',
        'bid_created': 'Zlecenie Utworzone',
        'bid_deleted': 'Zlecenie Usunięte',
        'files': 'Pliki',
        'attach_files': 'Załącz Pliki',
        
        # Wykonawcy
        'performers_catalog': 'Katalog Wykonawców',
        'days_on_service': 'Dni w Serwisie',
        'categories': 'Kategorie',
        'subcategories': 'Podkategorie',
        'contact_performer': 'Kontakt',
        
        # Wiadomości
        'success': 'Sukces',
        'error': 'Błąd',
        'loading': 'Ładowanie...',
        'no_results': 'Nie znaleziono wyników',
        'try_again': 'Spróbuj ponownie',
        
        # Uwierzytelnianie
        'sign_in': 'Zaloguj się',
        'sign_up': 'Zarejestruj się',
        'forgot_password': 'Zapomniałeś hasła?',
        'reset_password': 'Zresetuj hasło',
        'confirm_email': 'Potwierdź email',
        'verification_code': 'Kod weryfikacyjny',
        'resend_code': 'Wyślij ponownie kod',
        
        # Walidacja
        'field_required': 'Pole jest wymagane',
        'invalid_email': 'Nieprawidłowy email',
        'password_too_short': 'Hasło za krótkie',
        'passwords_not_match': 'Hasła nie pasują',
        'invalid_code': 'Nieprawidłowy kod',
        
        # Filtry
        'filter_by_category': 'Filtruj według kategorii',
        'filter_by_subcategory': 'Filtruj według podkategorii',
        'filter_by_city': 'Filtruj według miasta',
        'filter_by_date': 'Filtruj według daty',
        
        # Tłumaczenie
        'auto_translated': '(auto-tłumaczenie)',
        'translation_marker': '(przetłumaczone)',
        'original_language': 'Język oryginalny',
        'show_other_languages': 'Pokaż inne języki',
        'hide_other_languages': 'Ukryj inne języki',
    }
}

def get_translation(key: str, lang: str = 'uk') -> str:
    """
    Получает перевод для указанного ключа и языка.
    Если перевод не найден, возвращает ключ.
    """
    return TRANSLATIONS.get(lang, {}).get(key, key)

def get_all_translations(lang: str = 'uk') -> dict:
    """
    Возвращает все переводы для указанного языка.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS['uk'])

def translate_category_name(category, lang: str = 'uk') -> str:
    """
    Возвращает название категории на указанном языке.
    """
    if not category:
        return ''
    
    if hasattr(category, f'name_{lang}'):
        return getattr(category, f'name_{lang}', '') or category.name_uk or category.name or ''
    
    return str(category)

def translate_subcategory_name(subcategory, lang: str = 'uk') -> str:
    """
    Возвращает название подкатегории на указанном языке.
    """
    if not subcategory:
        return ''
    
    if hasattr(subcategory, f'name_{lang}'):
        return getattr(subcategory, f'name_{lang}', '') or subcategory.name_uk or ''
    
    return str(subcategory) 