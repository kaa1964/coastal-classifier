"""
Главное окно приложения с картой Folium
"""

import sys
import os
import tempfile
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QSplitter, QLabel, 
                               QPushButton, QComboBox, QTextEdit,
                               QGroupBox, QFormLayout, QMessageBox,
                               QStatusBar)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction

# Для веб-движка - правильный импорт для PySide6
try:
    # QWebEngineView находится в QtWebEngineWidgets
    from PySide6.QtWebEngineWidgets import QWebEngineView
    
    # Остальные классы - в QtWebEngineCore
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    
    print("✓ QtWebEngine импортирован успешно")
    print("  - QWebEngineView из QtWebEngineWidgets")
    print("  - QWebEngineCore для вспомогательных классов")
    
except ImportError as e:
    print(f"✗ ОШИБКА: QtWebEngine не найден! {e}")
    print("Убедитесь, что установлены пакеты: PySide6, PySide6-Addons")
    print("Текущие пакеты PySide6:")
    import subprocess
    subprocess.run(["pip", "list | grep PySide"], shell=True)
    sys.exit(1)

import folium
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config_manager import get_config_manager
from src.utils.i18n import get_i18n

######################
class MapView(QWebEngineView):
    """Виджет для отображения карты Folium"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Создаем временную папку
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        print(f"✓ Создана временная папка: {self.temp_dir}")
        
        # Путь к HTML файлу карты
        self.map_path = os.path.join(self.temp_dir, 'map.html')
        print(f"✓ Путь к карте: {self.map_path}")
        
        self.current_map = None
        
        # Настройки веб-виджета
        self.settings().setAttribute(self.settings().WebAttribute.LocalContentCanAccessFileUrls, True)
        self.settings().setAttribute(self.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        # Инициализируем карту
        self.init_map()
        
        # Подключаем сигнал загрузки
        self.loadFinished.connect(self.on_load_finished)
    
    def on_load_finished(self, ok):
        """Вызывается когда страница загружена"""
        if ok:
            print(f"✓ Карта загружена успешно: {self.map_path}")
        else:
            print(f"✗ Ошибка загрузки карты: {self.map_path}")
    
    def init_map(self, lat=20.0, lon=110.0, zoom=5):
        """Инициализация карты"""
        print(f"\n--- Инициализация карты ---")
        print(f"Параметры: lat={lat}, lon={lon}, zoom={zoom}")
        
        try:
            # Создаем карту Folium
            self.current_map = folium.Map(
                location=[lat, lon],
                zoom_start=zoom,
                tiles='OpenStreetMap',
                control_scale=True
            )
            print("✓ Карта Folium создана")
            
            # Добавляем обработчик кликов
            self.current_map.add_child(folium.LatLngPopup())
            print("✓ Обработчик кликов добавлен")
            
            # Сохраняем временный HTML файл
            self.current_map.save(self.map_path)
            print(f"✓ Карта сохранена в: {self.map_path}")
            
            # Проверяем, существует ли файл
            if os.path.exists(self.map_path):
                file_size = os.path.getsize(self.map_path)
                print(f"✓ Файл существует, размер: {file_size} байт")
                
                # Покажем первые несколько строк файла для проверки
                try:
                    with open(self.map_path, 'r', encoding='utf-8') as f:
                        first_lines = ''.join([f.readline() for _ in range(5)])
                    print(f"Первые строки HTML:\n{first_lines}")
                except Exception as e:
                    print(f"Не удалось прочитать файл: {e}")
            else:
                print("✗ ФАЙЛ НЕ СОЗДАН!")
                return
            
            # Загружаем в веб-виджет
            url = QUrl.fromLocalFile(self.map_path)
            print(f"Загружаем URL: {url.toString()}")
            self.load(url)
            
        except Exception as e:
            print(f"✗ ОШИБКА при создании карты: {e}")
            import traceback
            traceback.print_exc()
    
    def add_marker(self, lat, lon, popup_text=None):
        """Добавляет маркер на карту"""
        if self.current_map:
            try:
                folium.Marker(
                    [lat, lon],
                    popup=popup_text or f"{lat:.4f}, {lon:.4f}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(self.current_map)
                self.current_map.save(self.map_path)
                self.reload()
                print(f"✓ Маркер добавлен: {lat}, {lon}")
            except Exception as e:
                print(f"✗ Ошибка добавления маркера: {e}")
    
    def clear_markers(self):
        """Очищает все маркеры"""
        try:
            # Пересоздаем карту без маркеров
            center = self.current_map.location if self.current_map else [20.0, 110.0]
            zoom = self.current_map.zoom_start if self.current_map else 5
            self.init_map(center[0], center[1], zoom)
            print("✓ Маркеры очищены")
        except Exception as e:
            print(f"✗ Ошибка очистки маркеров: {e}")
    
    def get_zoom(self):
        """Возвращает текущий зум (заглушка)"""
        return 5
    
    def get_center(self):
        """Возвращает центр карты (заглушка)"""
        return [20.0, 110.0]
##############################
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
        
        # Создаем сплиттер для изменения размеров
        splitter = QSplitter(Qt.Horizontal)
        
        # ===== Левая панель - карта =====
        self.map_view = MapView(self)
        splitter.addWidget(self.map_view)
        
        # ===== Правая панель - информация и управление =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Информация о пользователе и сессии
        self.add_user_info_panel(right_layout)
        
        # Информация о выбранной точке
        self.add_point_info_panel(right_layout)
        
        # Панель классов
        self.add_class_panel(right_layout)
        
        # Кнопки управления
        self.add_control_buttons(right_layout)
        
        # История действий
        self.add_history_panel(right_layout)
        
        splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции (карта занимает 70% ширины)
        splitter.setSizes([840, 360])  # 70% и 30%
        
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
        
        # Высота (будет получена из API)
        self.elevation_label = QLabel("...")
        group_layout.addRow(self.i18n.t('elevation'), self.elevation_label)
        
        # Дополнительная информация (будет расширяться)
        self.extra_info = QTextEdit()
        self.extra_info.setReadOnly(True)
        self.extra_info.setMaximumHeight(100)
        group_layout.addRow("API Data:", self.extra_info)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
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
        self.add_button.clicked.connect(self.on_add_point)
        group_layout.addWidget(self.add_button)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_control_buttons(self, layout):
        """Кнопки управления"""
        button_layout = QHBoxLayout()
        
        # Отмена последнего действия
        self.undo_button = QPushButton(self.i18n.t('undo'))
        self.undo_button.clicked.connect(self.on_undo)
        self.undo_button.setEnabled(False)
        button_layout.addWidget(self.undo_button)
        
        # Экспорт
        self.export_button = QPushButton(self.i18n.t('export'))
        self.export_button.clicked.connect(self.on_export)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        # Выход
        self.exit_button = QPushButton(self.i18n.t('exit_without_save'))
        self.exit_button.clicked.connect(self.on_exit)
        layout.addWidget(self.exit_button)
    
    def add_history_panel(self, layout):
        """Панель истории действий"""
        group = QGroupBox("History")
        group_layout = QVBoxLayout()
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(150)
        group_layout.addWidget(self.history_text)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def update_status(self):
        """Обновляет статусную строку"""
        status = f"Points: {len(self.session_points)} | User: {self.user_data['first_name']} {self.user_data['last_name']} | Session: {self.user_data['session_number']}"
        self.status_bar.showMessage(status)
    
    def on_add_point(self):
        """Обработка добавления точки"""
        # TODO: Получить координаты из карты
        # TODO: Получить данные из API
        # TODO: Сохранить точку
        
        # Пока просто заглушка
        self.session_points.append({
            'timestamp': datetime.now().isoformat(),
            'class': self.class_combo.currentData()
        })
        
        self.points_label.setText(str(len(self.session_points)))
        self.undo_button.setEnabled(True)
        
        # Добавляем в историю
        self.history_text.append(f"Added point #{len(self.session_points)}")
        
        self.update_status()
    
    def on_undo(self):
        """Отмена последнего действия"""
        if self.session_points:
            removed = self.session_points.pop()
            self.history_text.append(f"Undid point #{len(self.session_points) + 1}")
            self.points_label.setText(str(len(self.session_points)))
            
            if not self.session_points:
                self.undo_button.setEnabled(False)
            
            self.update_status()
    
    def on_export(self):
        """Экспорт данных в GeoJSON"""
        # TODO: Реализовать экспорт
        QMessageBox.information(self, "Export", "Export functionality will be implemented")
    
    def on_exit(self):
        """Выход из приложения"""
        if self.session_points:
            reply = QMessageBox.question(
                self, 'Exit',
                self.i18n.t('confirm_exit'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.close()
        else:
            self.close()


# Для тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Тестовые данные пользователя
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