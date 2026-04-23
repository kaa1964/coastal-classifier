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
        # Добавить после 'elevation': 'Высота/глубина:',
        'details': 'Детали',
        'point_coordinates': '📍 Координаты:',
        'depth_value': '🌊 Глубина: {value} м (NOAA)',
        'elevation_value': '⛰️ Высота: {value} м (NOAA)',
        'elevation_srtm': '⛰️ Высота: {value} м (SRTM)',
        'distance_to_coast': '🏖️ Расстояние до берега: {dist} км',
        'distance_no_data': '🏖️ Расстояние до берега: данные отсутствуют в этом регионе',
        'distance_failed': '🏖️ Расстояние до берега: не удалось вычислить',
        'objects_in_radius': '🏗️ Объекты в радиусе 10 км:',
        'objects_not_found': '🏝️ Объекты в радиусе 10 км: не найдены',
        'total_objects': 'Всего объектов: {count}',
        # Названия объектов
        'piers': 'Пирсы',
        'lighthouses': 'Маяки',
        'breakwaters': 'Волнорезы',
        'harbors': 'Порты',
        'rivers': 'Реки',
        'lakes': 'Озера',
        'beaches': 'Пляжи',
        'cliffs': 'Утесы',
        'industrial': 'Промзоны',

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
        
        'point_coordinates': '📍 Coordinates:',
        'depth_value': '🌊 Depth: {value} m (NOAA)',
        'elevation_value': '⛰️ Elevation: {value} m (NOAA)',
        'elevation_srtm': '⛰️ Elevation: {value} m (SRTM)',
        'distance_to_coast': '🏖️ Distance to coast: {dist} km',
        'distance_no_data': '🏖️ Distance to coast: no data in this region',
        'distance_failed': '🏖️ Distance to coast: could not calculate',
        'objects_in_radius': '🏗️ Objects within 10 km radius:',
        'objects_not_found': '🏝️ Objects within 10 km radius: not found',
        'total_objects': 'Total objects: {count}',
        # Названия объектов
        'details': 'Details',
        'piers': 'Piers',
        'lighthouses': 'Lighthouses',
        'breakwaters': 'Breakwaters',
        'harbors': 'Harbors',
        'rivers': 'Rivers',
        'lakes': 'Lakes',
        'beaches': 'Beaches',
        'cliffs': 'Cliffs',
        'industrial': 'Industrial zones',

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
    },


    # 👇 НАЧАЛО БЛОКА СЛОВАРЯ ДЛЯ КИТАЙСКОГО ЯЗЫКА
    'zh': {
        'app_name': 'Coastal Classifier',
        'ok': '确定',
        'cancel': '取消',
        'save': '保存',
        'exit': '退出',
        
        'registration_title': '用户注册',
        'first_name': '名字:',
        'last_name': '姓氏:',
        'registration_date': '注册日期:',
        'filename_preview': '保存文件名:',
        'start_button': '开始工作',
        'fill_name_warning': '请输入名字',
        'fill_lastname_warning': '请输入姓氏',
        'filename_placeholder': '请输入名字和姓氏',
        
        'language': '语言',
        'russian': '俄语',
        'english': '英语',
        
        'main_window_title': 'Coastal Classifier - 沿海区域标注',
        'current_user': '用户:',
        'current_session': '会话:',
        'points_marked': '已标注点数:',
        'select_point': '在地图上选择点',
        'point_info': '点信息',
        'latitude': '纬度:',
        'longitude': '经度:',
        'elevation': '海拔/深度:',
        'point_coordinates': '📍 坐标:',
        'depth_value': '🌊 深度: {value} 米 (NOAA)',
        'elevation_value': '⛰️ 海拔: {value} 米 (NOAA)',
        'elevation_srtm': '⛰️ 海拔: {value} 米 (SRTM)',
        'distance_to_coast': '🏖️ 到海岸距离: {dist} 公里',
        'distance_no_data': '🏖️ 到海岸距离: 该区域无数据',
        'distance_failed': '🏖️ 到海岸距离: 无法计算',
        'objects_in_radius': '🏗️ 半径10公里内的对象:',
        'objects_not_found': '🏝️ 半径10公里内: 未找到对象',
        'total_objects': '对象总数: {count}',
        # Названия объектов
        'details': '详细信息',
        'piers': '码头',
        'lighthouses': '灯塔',
        'breakwaters': '防波堤',
        'harbors': '港口',
        'rivers': '河流',
        'lakes': '湖泊',
        'beaches': '海滩',
        'cliffs': '悬崖',
        'industrial': '工业区',

        'class_selection': '点的类别:',
        'classes': {
            'OPEN_SEA': '公海',
            'COASTAL_SEA': '近海水域',
            'NEAR_COAST': '近岸陆地',
            'COASTLINE': '内陆',
        },
        'add_point': '添加点',
        'undo': '撤销',
        'export': '导出为 GeoJSON',
        'exit_without_save': '退出',
        
        'confirm_exit': '有未保存的数据。确定要退出吗？',
        'export_success': '数据已成功导出到 {filename}',
        'export_error': '导出数据时出错',
        'api_error': 'API 请求错误: {error}',
    },   # <-- НЕ ЗАБУДЬТЕ ЗАПЯТУЮ В КОНЦЕ НОВОГО БЛОКА

}  # <-- конец блока словаря для китайского языка





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
