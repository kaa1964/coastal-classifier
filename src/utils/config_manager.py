"""
Менеджер конфигурации приложения
Сохраняет настройки пользователя между сеансами
Поддерживает русский и английский языки
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Управляет сохранением и загрузкой настроек приложения"""
    
    # Доступные языки
    LANGUAGES = {
        'ru': 'Русский',
        'en': 'English'
    }
    
    def __init__(self):
        # Определяем путь к файлу конфигурации
        self.config_dir = Path.home() / '.coastal-classifier'
        self.config_file = self.config_dir / 'config.json'
        
        # Создаем папку для конфигурации, если её нет
        self.config_dir.mkdir(exist_ok=True)
        
        # Загружаем или создаем конфигурацию
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Загружает конфигурацию из файла"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def save(self) -> None:
        """Сохраняет текущую конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию по умолчанию"""
        import getpass
        
        return {
            'user': {
                'first_name': '',
                'last_name': '',
                'last_session_date': '',
                'sessions_count': 0
            },
            'app': {
                'language': 'ru',  # По умолчанию русский
                'last_region': {
                    'lat': 20.0,
                    'lon': 110.0,
                    'zoom': 5
                },
                'window': {
                    'width': 1200,
                    'height': 800,
                    'maximized': False
                }
            },
            'api': {
                'use_cache': True,
                'timeout': 10,
                'retry_count': 3
            }
        }
    
    def get_user_data(self) -> Dict[str, str]:
        """Возвращает сохраненные данные пользователя"""
        return self.config.get('user', {})
    
    def set_user_data(self, first_name: str, last_name: str) -> None:
        """Сохраняет данные пользователя"""
        from datetime import datetime
        
        self.config['user']['first_name'] = first_name
        self.config['user']['last_name'] = last_name
        self.config['user']['last_session_date'] = datetime.now().strftime('%Y-%m-%d')
        self.config['user']['sessions_count'] = self.config['user'].get('sessions_count', 0) + 1
        self.save()
    
    def get_language(self) -> str:
        """Возвращает текущий язык интерфейса"""
        return self.config.get('app', {}).get('language', 'ru')
    
    def set_language(self, language: str) -> None:
        """Устанавливает язык интерфейса"""
        if language in self.LANGUAGES:
            self.config['app']['language'] = language
            self.save()
    
    def get_last_region(self) -> Dict[str, float]:
        """Возвращает последний просмотренный регион на карте"""
        return self.config.get('app', {}).get('last_region', {
            'lat': 20.0, 'lon': 110.0, 'zoom': 5
        })
    
    def set_last_region(self, lat: float, lon: float, zoom: int) -> None:
        """Сохраняет последний просмотренный регион"""
        self.config['app']['last_region'] = {
            'lat': lat, 'lon': lon, 'zoom': zoom
        }
        self.save()
    
    def get_next_session_filename(self) -> str:
        """Генерирует имя файла для следующей сессии"""
        user = self.config.get('user', {})
        first = user.get('first_name', '')
        last = user.get('last_name', '')
        session_num = user.get('sessions_count', 0) + 1
        
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        
        if first and last:
            return f"{last.upper()}_{first.capitalize()}_{date_str}_session{session_num:03d}.geojson"
        else:
            return f"user_{date_str}_session{session_num:03d}.geojson"


# Глобальный экземпляр менеджера конфигурации
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Возвращает глобальный экземпляр менеджера конфигурации"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager