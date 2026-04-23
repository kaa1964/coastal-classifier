"""
Главное окно приложения с картой Folium
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QSplitter, QLabel, 
                               QPushButton, QComboBox, QTextEdit,
                               QGroupBox, QFormLayout, QMessageBox,
                               QStatusBar)
from PySide6.QtCore import Qt, QUrl, Signal, Slot, QTimer
from PySide6.QtGui import QAction

import folium
from folium import ClickForMarker  # Добавьте эту строку

from src.gui.map_widget import MapWidget  # ЭТО НУЖНО ДОБАВИТЬ
# from src.api.elevation_api import ElevationAPI
from src.api.overpass_api import OverpassAPI
from src.api.noaa_api import NOAAAPI

# Для веб-движка
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    from PySide6.QtWebChannel import QWebChannel
    print("✓ QtWebEngine импортирован успешно")
except ImportError as e:
    print(f"✗ ОШИБКА: QtWebEngine не найден! {e}")
    sys.exit(1)

import folium

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config_manager import get_config_manager
from src.utils.i18n import get_i18n

from src.api.elevation_api import ElevationAPI

from src.api.copernicus_api import get_bathymetry
from src.core.geojson_exporter import GeoJSONExporter

##################################################


##################################################
class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, user_data):
        super().__init__()
        
        # Сохраняем данные пользователя
        self.user_data = user_data
        self.config = get_config_manager()
        self.i18n = get_i18n()
        
        # Данные сессии
        self.session_points = []  # Список размеченных точек
        self.current_point = None  # Текущая выбранная точка
        self.temp_point = None  # Временная точка для предпросмотра


        
        # Настройки окна
        self.setWindowTitle(self.i18n.t('main_window_title'))
        self.resize(1200, 800)
        
        # Центрируем окно
        self.center_window()
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        print("\n✓ ГЛАВНОЕ ОКНО ГОТОВО")
        print("="*50)
        
        # Добавить эту строку
        # self.elevation_api = ElevationAPI()
        
        self.overpass = OverpassAPI()
        self.elevation_api = ElevationAPI()
        self.noaa_api = NOAAAPI()

    
    def center_window(self):
        """Центрирует окно на экране"""
        screen = self.screen().availableGeometry()
        self.setGeometry(
            (screen.width() - 1200) // 2,
            (screen.height() - 800) // 2,
            1200, 800
        )
    
    def setup_ui(self):
        """Создание интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем сплиттер
        splitter = QSplitter(Qt.Horizontal)
        
        # ===== Левая панель - карта =====
        print("Создание виджета карты...")
        # self.map_view = MapView(self)
        self.map_view = MapWidget(self)
        # self.map_view.coordinates_clicked.connect(self.on_map_click)
        self.map_view.mapClicked.connect(self.on_map_click)
        
        # ЭТО ВАЖНО!
        print("✓ Сигнал карты подключен к MainWindow")
        
        splitter.addWidget(self.map_view)
        print("✓ Виджет карты создан")
        
        # ===== Правая панель =====
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)
        right_panel.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        
        # Информация о пользователе
        self.add_user_info_panel(right_layout)
        
        # Информация о точке
        self.add_point_info_panel(right_layout)
        
        # Панель классов
        self.add_class_panel(right_layout)
        
        # Кнопки управления
        self.add_control_buttons(right_layout)
        
        # История
        self.add_history_panel(right_layout)
        
        # Растягивающийся элемент в конце
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
    
    def add_user_info_panel(self, layout):
        """Панель информации о пользователе"""
        group = QGroupBox(self.i18n.t('current_user'))
        group_layout = QFormLayout()
        
        # Имя пользователя
        user_text = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        group_layout.addRow(self.i18n.t('current_user') + ":", QLabel(user_text))
        
        # Сессия
        session_text = f"#{self.user_data['session_number']} ({self.user_data['date']})"
        group_layout.addRow(self.i18n.t('current_session') + ":", QLabel(session_text))
        
        # Количество точек
        self.points_label = QLabel("0")
        group_layout.addRow(self.i18n.t('points_marked') + ":", self.points_label)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    #################################################################
    def add_point_info_panel(self, layout):
        """Панель информации о выбранной точке"""
        group = QGroupBox(self.i18n.t('point_info'))
        group_layout = QFormLayout()
        
        # Широта
        self.lat_label = QLabel("-")
        group_layout.addRow(self.i18n.t('latitude'), self.lat_label)
        
        # Долгота
        self.lon_label = QLabel("-")
        group_layout.addRow(self.i18n.t('longitude'), self.lon_label)
        
        # Высота/глубина
        self.elevation_label = QLabel("-")
        group_layout.addRow(self.i18n.t('elevation'), self.elevation_label)
        
        # Дополнительная информация (объекты OSM, источники данных)
        self.extra_info = QTextEdit()
        self.extra_info.setReadOnly(True)
        self.extra_info.setMaximumHeight(200)
        self.extra_info.setMinimumHeight(100)
        self.extra_info.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        #group_layout.addRow("Детали:", self.extra_info)
        group_layout.addRow(self.i18n.t('details') + ":", self.extra_info)

        group.setLayout(group_layout)
        layout.addWidget(group)
        


    ######################################################
    def add_class_panel(self, layout):
        """Панель выбора класса"""
        group = QGroupBox(self.i18n.t('class_selection'))
        group_layout = QVBoxLayout()
        
        # Выпадающий список классов
        self.class_combo = QComboBox()
        classes = self.i18n.t('classes')
        self.class_combo.addItem(classes['OPEN_SEA'], 'OPEN_SEA')
        self.class_combo.addItem(classes['COASTAL_SEA'], 'COASTAL_SEA')
        self.class_combo.addItem(classes['NEAR_COAST'], 'NEAR_COAST')
        self.class_combo.addItem(classes['COASTLINE'], 'COASTLINE')
        group_layout.addWidget(self.class_combo)
        
        # Кнопка добавления
        self.add_button = QPushButton(self.i18n.t('add_point'))
        self.add_button.setEnabled(False)

        self.add_button.clicked.connect(self.on_add_point)
        group_layout.addWidget(self.add_button)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_control_buttons(self, layout):
        """Кнопки управления"""
        # Кнопки в ряд
        button_layout = QHBoxLayout()
        
        self.undo_button = QPushButton(self.i18n.t('undo'))
        self.undo_button.clicked.connect(self.on_undo)
        self.undo_button.setEnabled(False)
        button_layout.addWidget(self.undo_button)
        
        self.export_button = QPushButton(self.i18n.t('export'))
        self.export_button.clicked.connect(self.on_export)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        # Кнопка выхода
        self.exit_button = QPushButton(self.i18n.t('exit'))
        self.exit_button.clicked.connect(self.on_exit)
        layout.addWidget(self.exit_button)
    
    def add_history_panel(self, layout):
        """Панель истории"""
        group = QGroupBox("History")
        group_layout = QVBoxLayout()
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(150)
        group_layout.addWidget(self.history_text)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
######################################################    
    ####################
    @Slot(float, float)
    def on_map_click(self, lat, lon):
        """Обработка клика на карте"""
        print(f"\n🎯 ГЛАВНОЕ ОКНО: получены координаты {lat:.6f}, {lon:.6f}")
        
        # Получаем данные из API
        elevation = self.elevation_api.get_elevation(lat, lon)
        noaa_data = self.noaa_api.get_depth(lat, lon)
        osm_features = self.overpass.get_coastal_features(lat, lon)
     #############################################################   
        # Формируем текст для отображения в Деталях
        
        info_text = f"{self.i18n.t('point_coordinates')} {lat:.4f}, {lon:.4f}\n\n"

        # Высота/глубина
        if noaa_data:
            if noaa_data['value'] < 0:
                info_text += self.i18n.t('depth_value', value=f"{abs(noaa_data['value']):.1f}") + "\n"
            else:
                info_text += self.i18n.t('elevation_value', value=f"{noaa_data['value']:.1f}") + "\n"
        elif elevation is not None:
            info_text += self.i18n.t('elevation_srtm', value=f"{elevation:.1f}") + "\n"

        # Расстояние до берега
        if 'distance_to_coast_km' in osm_features:
            if osm_features['distance_to_coast_km'] is not None:
                dist = osm_features['distance_to_coast_km']
                info_text += self.i18n.t('distance_to_coast', dist=f"{dist:.1f}") + "\n"
            else:
                info_text += self.i18n.t('distance_no_data') + "\n"
        else:
            info_text += self.i18n.t('distance_failed') + "\n"

        # Объекты инфраструктуры
        if osm_features and osm_features.get('total_objects', 0) > 0:
            info_text += f"\n{self.i18n.t('objects_in_radius')}\n"
            
            object_names = {
                'piers': self.i18n.t('piers'),
                'lighthouses': self.i18n.t('lighthouses'),
                'breakwaters': self.i18n.t('breakwaters'),
                'harbors': self.i18n.t('harbors'),
                'rivers': self.i18n.t('rivers'),
                'lakes': self.i18n.t('lakes'),
                'beaches': self.i18n.t('beaches'),
                'cliffs': self.i18n.t('cliffs'),
                'industrial': self.i18n.t('industrial')
            }
            
            for key, name in object_names.items():
                if key in osm_features and osm_features[key] > 0:
                    info_text += f"  • {name}: {osm_features[key]}\n"
            
            info_text += f"\n  {self.i18n.t('total_objects', count=osm_features.get('total_objects', 0))}"
        else:
            info_text += f"\n{self.i18n.t('objects_not_found')}"


     ############################################################## 
        
        # Сохраняем временную точку
        self.temp_point = {
            'lat': lat,
            'lon': lon,
            'elevation': elevation,
            'noaa': noaa_data,
            'osm_features': osm_features
        }
        
        # Обновляем интерфейс
        self.update_point_info(self.temp_point)
        self.extra_info.setText(info_text)
        
        # Добавляем временный маркер
        self.map_view.add_temp_marker(lat, lon, "Предпросмотр")
        self.add_button.setEnabled(True)
        
        print("✓ Точка предпросмотра. Выберите класс и нажмите 'Добавить точку'")

    ###########################
#########################################

    def on_add_point(self):
        if not hasattr(self, 'temp_point') or not self.temp_point:
            QMessageBox.warning(self, "Внимание", "Сначала выберите точку на карте")
            return
        
        class_code = self.class_combo.currentData()
        class_name = self.class_combo.currentText()
        
        point = {
            'timestamp': datetime.now().isoformat(),
            'lat': self.temp_point['lat'],
            'lon': self.temp_point['lon'],
            'elevation': self.temp_point.get('elevation'),
            'noaa': self.temp_point.get('noaa'),
            'osm_features': self.temp_point.get('osm_features', {}),
            'class_code': class_code,
            'class_name': class_name,
            'number': len(self.session_points) + 1
        }
        
        self.session_points.append(point)
        
        self.map_view.clear_markers()
        for p in self.session_points:
            self.map_view.add_marker(p['lat'], p['lon'], f"#{p['number']}: {p['class_name']}")
        
        self.update_history()
        self.temp_point = None
        self.add_button.setEnabled(False)
        self.undo_button.setEnabled(True)
        self.update_status()
        
        print(f"✓ Точка #{point['number']} добавлена: {class_name}")


    ################################################
    def update_point_info(self, point):
        """Обновляет информацию о последней точке"""
        self.lat_label.setText(f"{point['lat']:.6f}°")
        self.lon_label.setText(f"{point['lon']:.6f}°")
        
        # Формируем текст для поля высоты/глубины
        if point.get('noaa'):
            value = point['noaa']['value']
            if value < 0:
                self.elevation_label.setText(f"↓ {abs(value):.1f} м (глубина)")
            else:
                self.elevation_label.setText(f"↑ {value:.1f} м (высота)")
        elif point.get('elevation') is not None:
            self.elevation_label.setText(f"↑ {point['elevation']:.1f} м (SRTM)")
        else:
            self.elevation_label.setText("н/д")

    def add_marker_to_map(self, point):
        """Добавляет маркер на карту"""
        self.map_view.add_marker(
            point['lat'], 
            point['lon'], 
            f"#{len(self.session_points)}: {point['class_name']}"
        )

    def update_history(self):
        """Обновляет историю точек"""
        self.history_text.clear()
        for i, point in enumerate(self.session_points, 1):
            class_name = point['class_name']
            depth_info = ""
            if point.get('noaa') and point['noaa']['value'] < 0:
                depth_info = f" (глуб.{abs(point['noaa']['value']):.0f}м)"
            self.history_text.append(f"{i}. {class_name}{depth_info}")
     
    ###############################################    
    def on_undo(self):
        if not self.session_points:
            return
        
        removed = self.session_points.pop()
        
        self.map_view.clear_markers()
        for point in self.session_points:
            self.map_view.add_marker(point['lat'], point['lon'], f"#{point['number']}: {point['class_name']}")
        
        if self.temp_point:
            self.map_view.add_temp_marker(self.temp_point['lat'], self.temp_point['lon'], "Предпросмотр")
        
        self.update_history()
        
        if self.session_points:
            self.update_point_info(self.session_points[-1])
        elif self.temp_point:
            self.update_point_info(self.temp_point)
        else:
            self.lat_label.setText("-")
            self.lon_label.setText("-")
            self.elevation_label.setText("-")
        
        self.undo_button.setEnabled(len(self.session_points) > 0)
        self.update_status()
        
        print(f"✓ Точка удалена. Осталось: {len(self.session_points)}")    
        
    
    
    ################################################
    def on_export(self):
        """Экспорт всех точек сессии в GeoJSON"""
        if not self.session_points:
            QMessageBox.information(self, "Экспорт", "Нет данных для экспорта")
            return
        
        # Создаем экспортер
        exporter = GeoJSONExporter(self.user_data)
        
        # Сохраняем файл
        filename = exporter.save_session(self.session_points)
        
        # Спрашиваем, очистить ли сессию после экспорта
        reply = QMessageBox.question(
            self, 'Экспорт завершен',
            f"✓ Экспортировано {len(self.session_points)} точек\n"
            f"Файл: {filename}\n\n"
            f"Очистить сессию?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Очищаем сессию
            self.session_points.clear()
            self.map_view.clear_markers()
            self.update_history()
            self.lat_label.setText("-")
            self.lon_label.setText("-")
            self.elevation_label.setText("-")
            self.undo_button.setEnabled(False)
            self.update_status()
            print("✓ Сессия очищена")
        
    ##############################################


    def on_exit(self):
        """Выход из приложения"""
        if self.session_points:
            reply = QMessageBox.question(
                self, 'Выход',
                self.i18n.t('confirm_exit'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.close()
        else:
            self.close()
    
    def update_status(self):
        """Обновление статусной строки"""
        status = f"Точек: {len(self.session_points)} | Пользователь: {self.user_data['first_name']} {self.user_data['last_name']} | Сессия: {self.user_data['session_number']}"
        self.status_bar.showMessage(status)


# Для тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    test_user = {
        'first_name': 'Иван',
        'last_name': 'ПЕТРОВ',
        'date': '2025-02-26',
        'date_int': '20250226',
        'filename': 'PETROV_Иван_20250226_session001.geojson',
        'session_number': 1
    }
    
    window = MainWindow(test_user)
    window.show()
    
    sys.exit(app.exec())