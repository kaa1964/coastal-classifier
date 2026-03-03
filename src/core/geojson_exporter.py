"""
Модуль для экспорта точек в GeoJSON
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class GeoJSONExporter:
    """Экспорт точек в формат GeoJSON"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.user_data = user_data
        self.filename = user_data.get('filename', 'points.geojson')
        
        # Создаем путь к папке sessions
        self.sessions_dir = os.path.join('data', 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Полный путь к файлу
        self.filepath = os.path.join(self.sessions_dir, self.filename)
    
    def create_feature(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """Создает GeoJSON feature из точки"""
        
        # Основные свойства
        properties = {
            'timestamp': point['timestamp'],
            'latitude': point['lat'],
            'longitude': point['lon'],
            'elevation': point.get('elevation'),
            'class_code': point['class_code'],
            'class_name': point['class_name'],
            'source_session': self.user_data.get('session_number')
        }
        
        # Добавляем NOAA данные если есть
        if point.get('noaa'):
            properties['noaa_depth'] = point['noaa']['value']
            properties['noaa_type'] = point['noaa']['type']
        
        # Добавляем объекты OSM
        if point.get('osm_features'):
            for key, value in point['osm_features'].items():
                properties[f'osm_{key}'] = value
        
        # GeoJSON feature
        feature = {
            'type': 'Feature',
            'properties': properties,
            'geometry': {
                'type': 'Point',
                'coordinates': [point['lon'], point['lat']]
            }
        }
        
        return feature
    
    def load_existing(self) -> List[Dict[str, Any]]:
        """Загружает существующие точки из файла"""
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('features', [])
        except:
            return []
    
    def save_session(self, points: List[Dict[str, Any]]) -> str:
        """
        Сохраняет сессию точек в новый файл
        (не дозаписывает, а создает новый файл сессии)
        """
        # Создаем новые features
        new_features = [self.create_feature(p) for p in points]
        
        # Создаем полный GeoJSON
        geojson = {
            'type': 'FeatureCollection',
            'name': self.filename.replace('.geojson', ''),
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'
                }
            },
            'features': new_features
        }
        
        # Сохраняем
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Сессия сохранена: {self.filepath}")
        print(f"✓ Точек в сессии: {len(points)}")
        
        return self.filepath