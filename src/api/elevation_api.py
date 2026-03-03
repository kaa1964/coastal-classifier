"""
Модуль для получения высоты точки через Open-Elevation API
"""

import requests
import time
from typing import Optional

class ElevationAPI:
    """Класс для работы с API высот"""
    
    def __init__(self):
        self.url = "https://api.open-elevation.com/api/v1/lookup"
        self.timeout = 10
        self.max_retries = 2
    
    def get_elevation(self, lat: float, lon: float) -> Optional[float]:
        """
        Получает высоту точки над уровнем моря
        
        Returns:
            float: высота в метрах (0 для моря) или None при ошибке
        """
        try:
            params = {
                'locations': f'{lat},{lon}'
            }
            
            print(f"Запрос высоты для {lat:.4f}, {lon:.4f}...")
            
            response = requests.get(
                self.url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                elevation = data['results'][0]['elevation']
                print(f"✓ Высота: {elevation:.1f} м")
                return elevation
            else:
                print(f"Ошибка API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    
    def get_elevation_batch(self, points: list, delay: float = 0.1) -> list:
        """
        Получает высоты для нескольких точек
        """
        results = []
        for i, (lat, lon) in enumerate(points):
            print(f"Точка {i+1}/{len(points)}...")
            elev = self.get_elevation(lat, lon)
            results.append(elev)
            if i < len(points) - 1:
                time.sleep(delay)
        return results


# Для тестирования
if __name__ == "__main__":
    api = ElevationAPI()
    
    test_points = [
        (55.75, 37.61),  # Москва
        (20.0, 110.0),   # Море
        (16.0, 108.0),   # Побережье Вьетнама
    ]
    
    print("="*50)
    print("Тест Open-Elevation API")
    print("="*50)
    
    for lat, lon in test_points:
        elev = api.get_elevation(lat, lon)
        status = "суша" if elev and elev > 0 else "море/0"
        print(f"  {lat:.2f}, {lon:.2f}: {elev} м ({status})")
        time.sleep(0.5)