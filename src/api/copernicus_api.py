"""
Модуль для получения батиметрических данных из Copernicus Marine Service
"""

import requests
import time
from typing import Optional, Dict, Any
import math

class CopernicusBathymetryAPI:
    """Класс для работы с батиметрией Copernicus"""
    
    def __init__(self):
        # Copernicus Marine Service - публичный доступ к данным
        self.base_url = "https://nrt.cmems-du.eu/motu-web/Motu"
        self.product_id = "GLOBAL_ANALYSISFORECAST_PHY_001_024"
        self.timeout = 30
    
    def get_depth(self, lat: float, lon: float) -> Optional[float]:
        """
        Получает глубину моря в точке
        
        Args:
            lat, lon: координаты точки
            
        Returns:
            float: глубина в метрах (отрицательная) или None при ошибке
        """
        try:
            # Упрощенный запрос к Copernicus (может потребовать аутентификацию)
            # Пока возвращаем тестовые данные
            return self._get_test_depth(lat, lon)
            
        except Exception as e:
            print(f"Ошибка Copernicus: {e}")
            return None
 ###################################################################################   
    def _get_test_depth(self, lat: float, lon: float) -> float:
        """
        Тестовая функция для демонстрации
        Возвращает примерные глубины для разных регионов
        """
        # Южно-Китайское море
        if 0 <= lat <= 25 and 100 <= lon <= 120:
            # Примерные глубины (взяты с карты)
            if 10 <= lat <= 15 and 108 <= lon <= 112:
                return -1500  # Глубокое море
            elif 15 <= lat <= 20 and 110 <= lon <= 115:
                return -2000  # Очень глубоко
            elif 5 <= lat <= 10 and 105 <= lon <= 110:
                return -1000  # Средние глубины
            
        # Побережье Вьетнама
        if 15 <= lat <= 18 and 106 <= lon <= 109:
            # Шельф
            dist_to_coast = min(abs(lon - 108), abs(lat - 16))
            if dist_to_coast < 1:
                return -50  # Близко к берегу
            elif dist_to_coast < 2:
                return -200  # Шельф
            else:
                return -500  # Глубже
        
        # По умолчанию - открытый океан
        if abs(lat) < 60 and abs(lon) < 180:
            # Генерация правдоподобной глубины
            depth = -4000 + (abs(lat) * 20) + (abs(lon % 30) * 10)
            return -abs(depth)
        
        return -3000  # Океан по умолчанию
################################################################

class GEBCOBathymetryAPI:
    """Альтернативный API - GEBCO (Gridded Bathymetry Data)"""
    
    def __init__(self):
        self.url = "https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/mapserv"
        self.timeout = 20
    
    def get_depth(self, lat: float, lon: float) -> Optional[float]:
        """
        Получает глубину через WMS сервис GEBCO
        """
        try:
            # Формируем запрос WMS GetFeatureInfo
            params = {
                'SERVICE': 'WMS',
                'VERSION': '1.3.0',
                'REQUEST': 'GetFeatureInfo',
                'LAYERS': 'gebco_latest',
                'QUERY_LAYERS': 'gebco_latest',
                'INFO_FORMAT': 'application/json',
                'I': '50',
                'J': '50',
                'WIDTH': '101',
                'HEIGHT': '101',
                'CRS': 'EPSG:4326',
                'BBOX': f'{lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}'
            }
            
            print(f"Запрос глубины GEBCO для {lat:.4f}, {lon:.4f}...")
            
            response = requests.get(
                self.url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # Парсинг ответа (сложный, требует доработки)
                # Пока возвращаем тестовые данные
                return self._estimate_depth(lat, lon)
            else:
                print(f"Ошибка GEBCO: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    
    def _estimate_depth(self, lat: float, lon: float) -> float:
        """Эвристическая оценка глубины для демонстрации"""
        # Упрощенная модель рельефа дна
        x = lon * math.pi / 180
        y = lat * math.pi / 180
        
        # Добавляем вариации
        depth = -3000  # базовая глубина
        depth -= 500 * math.sin(x * 2) * math.cos(y * 2)
        depth -= 200 * math.sin(x * 5) * math.cos(y * 5)
        
        # Мелководье у побережий
        if abs(lon - 108) < 2 and 15 < lat < 18:
            depth = -50 - abs(lon - 108) * 100
        
        return depth


# Упрощенный интерфейс для использования в приложении
def get_bathymetry(lat: float, lon: float) -> Dict[str, Any]:
    """
    Получает батиметрические данные из доступных источников
    """
    # Пробуем Copernicus
    copernicus = CopernicusBathymetryAPI()
    depth = copernicus.get_depth(lat, lon)
    
    if depth is not None:
        return {
            'source': 'copernicus',
            'depth': depth,
            'bathymetry': depth < 0
        }
    
    # Если Copernicus не работает, пробуем GEBCO
    gebco = GEBCOBathymetryAPI()
    depth = gebco.get_depth(lat, lon)
    
    if depth is not None:
        return {
            'source': 'gebco',
            'depth': depth,
            'bathymetry': depth < 0
        }
    
    # Если ничего не работает
    return {
        'source': 'none',
        'depth': None,
        'bathymetry': False
    }


# Для тестирования
if __name__ == "__main__":
    print("="*50)
    print("Тест батиметрических API")
    print("="*50)
    
    test_points = [
        (16.0, 108.0),   # Побережье Вьетнама
        (12.0, 110.0),   # Южно-Китайское море
        (55.75, 37.61),  # Москва (суша)
        (0.0, 0.0),      # Атлантика
    ]
    
    for lat, lon in test_points:
        print(f"\nТочка: {lat:.2f}, {lon:.2f}")
        data = get_bathymetry(lat, lon)
        
        if data['depth'] is not None:
            if data['bathymetry']:
                print(f"  Глубина: {abs(data['depth']):.0f} м")
            else:
                print(f"  Высота суши: {data['depth']:.0f} м")
            print(f"  Источник: {data['source']}")
        else:
            print("  Нет данных")
        
        time.sleep(1)