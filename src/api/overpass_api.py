"""
Модуль для работы с Overpass API (OpenStreetMap)
Оптимизированная версия с одним запросом
"""

import requests
import time
from typing import Dict, Optional, Any

class OverpassAPI:
    """Класс для запросов к OpenStreetMap через Overpass API"""
    
    def __init__(self):
        self.url = "https://overpass-api.de/api/interpreter"
        self.timeout = 30
        self.max_retries = 2
    
    def get_coastal_features(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Получает все признаки для точки одним запросом
        
        Args:
            lat, lon: координаты точки
            
        Returns:
            dict: словарь с найденными объектами
        """
        # Один сложный запрос вместо множества маленьких
        query = f"""
        [out:json][timeout:60];
        (
          // Пирсы
          node["man_made"="pier"](around:5000,{lat},{lon});
          way["man_made"="pier"](around:5000,{lat},{lon});
          
          // Маяки
          node["man_made"="lighthouse"](around:5000,{lat},{lon});
          way["man_made"="lighthouse"](around:5000,{lat},{lon});
          
          // Волнорезы
          node["man_made"="breakwater"](around:5000,{lat},{lon});
          way["man_made"="breakwater"](around:5000,{lat},{lon});
          
          // Порты
          node["harbor"="yes"](around:5000,{lat},{lon});
          way["harbor"="yes"](around:5000,{lat},{lon});
          
          // Реки
          node["waterway"="river"](around:5000,{lat},{lon});
          way["waterway"="river"](around:5000,{lat},{lon});
          
          // Озера
          node["natural"="water"](around:5000,{lat},{lon});
          way["natural"="water"](around:5000,{lat},{lon});
          
          // Пляжи
          node["natural"="beach"](around:5000,{lat},{lon});
          way["natural"="beach"](around:5000,{lat},{lon});
          
          // Утесы
          node["natural"="cliff"](around:5000,{lat},{lon});
          way["natural"="cliff"](around:5000,{lat},{lon});
          
          // Промышленные зоны
          node["landuse"="industrial"](around:5000,{lat},{lon});
          way["landuse"="industrial"](around:5000,{lat},{lon});
        );
        out body;
        """
        
        print(f"Запрос к Overpass API для точки {lat:.4f}, {lon:.4f}...")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.url,
                    params={'data': query},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_results(data)
                elif response.status_code == 429:
                    print(f"Слишком много запросов, ждем {attempt+1}с...")
                    time.sleep(attempt + 1)
                else:
                    print(f"Ошибка {response.status_code}")
                    return self._empty_result()
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                time.sleep(1)
        
        return self._empty_result()
    
    def _parse_results(self, data: Dict) -> Dict[str, int]:
        """Разбирает результаты запроса"""
        result = {
            'piers': 0,
            'lighthouses': 0,
            'breakwaters': 0,
            'harbors': 0,
            'rivers': 0,
            'lakes': 0,
            'beaches': 0,
            'cliffs': 0,
            'industrial': 0
        }
        
        if not data or 'elements' not in data:
            return result
        
        for element in data['elements']:
            tags = element.get('tags', {})
            
            # Проверяем теги
            if tags.get('man_made') == 'pier':
                result['piers'] += 1
            elif tags.get('man_made') == 'lighthouse':
                result['lighthouses'] += 1
            elif tags.get('man_made') == 'breakwater':
                result['breakwaters'] += 1
            elif tags.get('harbor') == 'yes':
                result['harbors'] += 1
            elif tags.get('waterway') == 'river':
                result['rivers'] += 1
            elif tags.get('natural') == 'water':
                result['lakes'] += 1
            elif tags.get('natural') == 'beach':
                result['beaches'] += 1
            elif tags.get('natural') == 'cliff':
                result['cliffs'] += 1
            elif tags.get('landuse') == 'industrial':
                result['industrial'] += 1
        
        return result
    
    def _empty_result(self):
        """Возвращает пустой результат"""
        return {
            'piers': 0,
            'lighthouses': 0,
            'breakwaters': 0,
            'harbors': 0,
            'rivers': 0,
            'lakes': 0,
            'beaches': 0,
            'cliffs': 0,
            'industrial': 0
        }


# Для тестирования
if __name__ == "__main__":
    api = OverpassAPI()
    
    # Тестовые точки
    test_points = [
        (16.0, 108.0),  # Побережье Вьетнама
        (21.0, 106.0),  # Северный Вьетнам
        (20.0, 110.0),  # Южно-Китайское море
    ]
    
    print("="*50)
    print("Тест Overpass API (оптимизированный)")
    print("="*50)
    
    for lat, lon in test_points:
        print(f"\nТочка: {lat:.2f}, {lon:.2f}")
        features = api.get_coastal_features(lat, lon)
        
        for key, value in features.items():
            if value > 0:
                print(f"  {key}: {value}")
        
        time.sleep(2)  # Задержка между точками