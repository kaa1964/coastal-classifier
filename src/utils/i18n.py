"""
Модуль интернационализации (i18n)
Поддерживает русский и английский языки
"""

from typing import Dict, Optional
from .config_manager import get_config_manager


# Словарь с переводами
TRANSLATIONS = {
    'ru': {
        # Общие
        'app_name': 'Coastal Classifier',
        'ok': 'OK',
        'cancel': 'Отмена',
        'save': 'Сохранить',
        'exit': 'Выход',
        
        # Окно регистрации
        'registration_title': 'Регистрация пользователя',
        'first_name': 'Имя:',
        'last_name': 'Фамилия:',
        'registration_date': 'Дата регистрации:',
        'filename_preview': 'Имя файла для сохранения:',
        'start_button': 'Начать работу',
        'fill_name_warning': 'Пожалуйста, введите имя',
        'fill_lastname_warning': 'Пожалуйста, введите фамилию',
        'filename_placeholder': 'Заполните имя и фамилию',
        
        # Язык
        'language': 'Язык / Language',
        'russian': 'Русский',
        'english': 'English',
        
        # Главное окно
        'main_window_title': 'Coastal Classifier - Разметка прибрежных зон',
        'current_user': 'Пользователь:',
        'current_session': 'Сессия:',
        'points_marked': 'Точек размечено:',
        'select_point': 'Выберите точку на карте',
        'point_info': 'Информация о точке',
        'latitude': 'Широта:',
        'longitude': 'Долгота:',
        'elevation': 'Высота/глубина:',  # замените существующую строку
        'class_selection': 'Класс точки:',
        'classes': {
            'OPEN_SEA': 'Открытое море',
            'COASTAL_SEA': 'Прибережье (море)',
            'NEAR_COAST': 'Побережье (суша)',
            'COASTLINE': 'Суша вдали от побережья'
        },
        'add_point': 'Добавить точку',
        'undo': 'Отменить',
        'export': 'Экспорт в GeoJSON',
        'exit_without_save': 'Выйти',
        
        # Сообщения
        'confirm_exit': 'Есть несохраненные данные. Вы уверены, что хотите выйти?',
        'export_success': 'Данные успешно экспортированы в {filename}',
        'export_error': 'Ошибка при экспорте данных',
        'api_error': 'Ошибка при запросе к API: {error}',
    },
    
    'en': {
        # Common
        'app_name': 'Coastal Classifier',
        'ok': 'OK',
        'cancel': 'Cancel',
        'save': 'Save',
        'exit': 'Exit',
        
        # Registration window
        'registration_title': 'User Registration',
        'first_name': 'First Name:',
        'last_name': 'Last Name:',
        'registration_date': 'Registration Date:',
        'filename_preview': 'Output filename:',
        'start_button': 'Start Working',
        'fill_name_warning': 'Please enter first name',
        'fill_lastname_warning': 'Please enter last name',
        'filename_placeholder': 'Enter first and last name',
        
        # Language
        'language': 'Language / Язык',
        'russian': 'Русский',
        'english': 'English',
        
        # Main window
        'main_window_title': 'Coastal Classifier - Coastal Zone Markup',
        'current_user': 'User:',
        'current_session': 'Session:',
        'points_marked': 'Points marked:',
        'select_point': 'Select a point on the map',
        'point_info': 'Point Information',
        'latitude': 'Latitude:',
        'longitude': 'Longitude:',
        'elevation': 'Elevation/Depth:',  # замените существующую строку
        'class_selection': 'Point Class:',
        'classes': {
            'OPEN_SEA': 'Open Sea',
            'COASTAL_SEA': 'Coastal Sea',
            'NEAR_COAST': 'Near Coast',
            'COASTLINE': 'Coastline'
        },
        'add_point': 'Add Point',
        'undo': 'Undo',
        'export': 'Export to GeoJSON',
        'exit_without_save': 'Exit',
        
        # Messages
        'confirm_exit': 'There are unsaved data. Are you sure you want to exit?',
        'export_success': 'Data successfully exported to {filename}',
        'export_error': 'Error exporting data',
        'api_error': 'API request error: {error}',
    }
}


class I18n:
    """Класс для работы с переводами"""
    
    def __init__(self):
        self.config = get_config_manager()
        self.current_language = self.config.get_language()
    
    def t(self, key: str, **kwargs) -> str:
        """
        Возвращает перевод для ключа
        Пример: i18n.t('hello', name='Иван')
        """
        # Получаем словарь для текущего языка
        lang_dict = TRANSLATIONS.get(self.current_language, TRANSLATIONS['ru'])
        
        # Разбиваем ключ по точкам для доступа к вложенным словарям
        parts = key.split('.')
        value = lang_dict
        
        try:
            for part in parts:
                value = value[part]
            
            # Подставляем параметры, если они есть
            if kwargs:
                return value.format(**kwargs)
            return value
            
        except (KeyError, TypeError):
            # Если перевод не найден, пробуем английский или возвращаем ключ
            if self.current_language != 'en':
                en_value = self._get_from_dict(TRANSLATIONS['en'], parts)
                if en_value:
                    return en_value.format(**kwargs) if kwargs else en_value
            return key
    
    def _get_from_dict(self, d: Dict, parts: list):
        """Вспомогательный метод для доступа к вложенным словарям"""
        value = d
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    def set_language(self, language: str) -> None:
        """Изменяет текущий язык"""
        if language in TRANSLATIONS:
            self.current_language = language
            self.config.set_language(language)


# Глобальный экземпляр
_i18n = None

def get_i18n() -> I18n:
    """Возвращает глобальный экземпляр переводчика"""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n