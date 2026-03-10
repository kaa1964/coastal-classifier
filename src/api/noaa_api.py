"""
Модуль для получения батиметрических данных из NOAA
С таймаутами и задержками
"""

import bathyreq
import time
import signal
from typing import Optional, Dict, Any

class TimeoutException(Exception):
    pass

class NOAAAPI:
    """Класс для работы с NOAA Bathymetry"""
    
    def __init__(self):
        """Инициализация клиента NOAA"""
        try:
            self.client = bathyreq.BathyRequest()
            self.available = True
            print("✓ NOAA API инициализирован")
            time.sleep(1)  # Задержка после инициализации
        except Exception as e:
            print(f"⚠️ NOAA API не доступен: {e}")
            self.available = False
            self.client = None
    
    def _timeout_handler(self, signum, frame):
        raise TimeoutException("Превышено время ожидания")

###########################################
    def get_depth(self, lat: float, lon: float, timeout_seconds: int = 30) -> Optional[Dict[str, Any]]:
            """
            Получает глубину/высоту из NOAA с таймаутом
            """
            if not self.available or not self.client:
                return None
            
            # Проверяем ОС
            import platform
            import threading
            import time
            
            is_windows = platform.system() == 'Windows'
            
            # Для Unix систем используем сигналы
            if not is_windows:
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(timeout_seconds)
            
            # Для Windows используем threading
            if is_windows:
                result_container = []
                exception_container = []
                completed = threading.Event()
                
                def worker():
                    try:
                        data = self.client.get_point(latitude=lat, longitude=lon)
                        result_container.append(data)
                    except Exception as e:
                        exception_container.append(e)
                    finally:
                        completed.set()
                
                thread = threading.Thread(target=worker)
                thread.daemon = True
                thread.start()
                
                if not completed.wait(timeout=timeout_seconds):
                    print(f"   ⏱️ Таймаут ({timeout_seconds}с)")
                    return None
                
                if exception_container:
                    print(f"   ❌ Ошибка: {exception_container[0]}")
                    return None
                
                data = result_container[0] if result_container else None
            else:
                # Для Unix - обычный код
                try:
                    print(f"Запрос NOAA для ({lat:.2f}, {lon:.2f})...")
                    data = self.client.get_point(latitude=lat, longitude=lon)
                    signal.alarm(0)
                except TimeoutException:
                    print(f"   ⏱️ Таймаут ({timeout_seconds}с)")
                    signal.alarm(0)
                    return None
                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")
                    signal.alarm(0)
                    return None
            
            # Единая обработка результата для обеих ОС
            print(f"   Получено: {data} (тип: {type(data)})")
            
            if data is not None:
                try:
                    if hasattr(data, '__len__') and len(data) > 0:
                        value = float(data[0])
                    elif isinstance(data, (int, float)):
                        value = float(data)
                    else:
                        print(f"   ⚠️ Неподдерживаемый тип: {type(data)}")
                        return None
                    
                    result = {
                        'value': value,
                        'type': 'depth' if value < 0 else 'height',
                        'source': 'NOAA',
                        'unit': 'м',
                        'note': 'NOAA Bathymetry'
                    }
                    
                    print(f"   ✓ {result['type']}: {abs(value):.1f} м")
                    return result
                    
                except Exception as e:
                    print(f"   ❌ Ошибка обработки: {e}")
                    return None
            
            print("   ⚠️ Нет данных")
            return None


###########################################
    # def get_depth(self, lat: float, lon: float, timeout_seconds: int = 30) -> Optional[Dict[str, Any]]:
    #     """
    #     Получает глубину/высоту из NOAA с таймаутом
    #     """
    #     if not self.available or not self.client:
    #         return None
        
    #     # Устанавливаем обработчик таймаута
    #     signal.signal(signal.SIGALRM, self._timeout_handler)
    #     signal.alarm(timeout_seconds)
        
    #     try:
    #         print(f"Запрос NOAA для ({lat:.2f}, {lon:.2f})...")
            
    #         # Выполняем запрос
    #         data = self.client.get_point(latitude=lat, longitude=lon)
            
    #         # Сбрасываем таймаут
    #         signal.alarm(0)
            
    #         print(f"   Получено: {data} (тип: {type(data)})")
            
    #         # Обрабатываем результат
    #         if data is not None:
    #             # Извлекаем значение из numpy array
    #             if hasattr(data, '__len__') and len(data) > 0:
    #                 value = float(data[0])
    #             elif isinstance(data, (int, float)):
    #                 value = float(data)
    #             else:
    #                 print(f"   ⚠️ Неподдерживаемый тип: {type(data)}")
    #                 return None
                
    #             result = {
    #                 'value': value,
    #                 'type': 'depth' if value < 0 else 'height',
    #                 'source': 'NOAA',
    #                 'unit': 'м',
    #                 'note': 'NOAA Bathymetry'
    #             }
                
    #             print(f"   ✓ {result['type']}: {abs(value):.1f} м")
    #             return result
            
    #         print("   ⚠️ Нет данных")
    #         return None
            
    #     except TimeoutException:
    #         print(f"   ⏱️ Таймаут ({timeout_seconds}с)")
    #         signal.alarm(0)
    #         return None
    #     except Exception as e:
    #         print(f"   ❌ Ошибка: {e}")
    #         signal.alarm(0)
    #         return None


 ########################################################

    def get_batch(self, points: list, delay: float = 3.0) -> list:
        """
        Получает данные для нескольких точек с задержкой
        """
        results = []
        total = len(points)
        
        for i, (lat, lon) in enumerate(points):
            print(f"\n📍 Точка {i+1}/{total} ({lat:.2f}, {lon:.2f})")
            
            result = self.get_depth(lat, lon)
            results.append(result)
            
            # Задержка между запросами (кроме последнего)
            if i < total - 1:
                print(f"⏳ Ожидание {delay}с...")
                time.sleep(delay)
        
        return results


# Для тестирования
if __name__ == "__main__":
    print("="*50)
    print("ТЕСТ NOAA API (с таймаутами)")
    print("="*50)
    
    api = NOAAAPI()
    
    test_points = [
        (19.27, 114.61, "Южно-Китайское море"),
        (16.00, 108.00, "Побережье Вьетнама"),
        (23.60, 120.85, "Тайвань"),
        (10.00, 106.00, "Дельта Меконга"),
    ]
    
    results = api.get_batch([(lat, lon) for lat, lon, _ in test_points])
    
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ")
    print("="*50)
    
    for (lat, lon, name), result in zip(test_points, results):
        if result:
            arrow = "↓" if result['type'] == 'depth' else "↑"
            print(f"\n📍 {name}: {arrow} {abs(result['value']):.1f} м")
        else:
            print(f"\n📍 {name}: ❌ нет данных")