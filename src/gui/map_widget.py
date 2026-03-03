"""
Виджет карты на основе Leaflet
"""

import tempfile
import folium
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl, Signal, Slot, QObject
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

# HTML шаблон карты
MAP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div id="map" style="height: 100vh; width: 100vw;"></div>
    <script>
        // Создаем карту
        var map = L.map('map').setView([{lat}, {lon}], {zoom});
        L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap'
        }}).addTo(map);
        
        // Подключаемся к WebChannel
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            var bridge = channel.objects.bridge;
            
            // Добавляем обработчик клика
            map.on('click', function(e) {{
                bridge.sendCoords(e.latlng.lat, e.latlng.lng);
            }});
            
            console.log('Карта готова');
        }});
    </script>
</body>
</html>
"""

class MapBridge(QObject):
    """Мост для связи JavaScript и Python"""
    
    coordsReceived = Signal(float, float)
    
    @Slot(float, float)
    def sendCoords(self, lat, lon):
        """Вызывается из JavaScript при клике на карту"""
        self.coordsReceived.emit(lat, lon)


class MapWidget(QWidget):
    """Виджет карты с поддержкой кликов и маркеров"""
    
    mapClicked = Signal(float, float)
    
    def __init__(self, parent=None, lat=20.0, lon=110.0, zoom=5):
        super().__init__(parent)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем веб-виджет
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Настройки веб-виджета
        settings = self.web_view.settings()
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        
        # Создаем мост
        self.bridge = MapBridge()
        self.bridge.coordsReceived.connect(self.on_coords_received)
        
        # Настраиваем WebChannel
        self.channel = QWebChannel(self.web_view)
        self.web_view.page().setWebChannel(self.channel)
        self.channel.registerObject("bridge", self.bridge)
        
        # Создаем HTML
        html = MAP_HTML.format(lat=lat, lon=lon, zoom=zoom)
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
            f.write(html)
            self.temp_path = f.name
        
        # Загружаем карту
        self.web_view.load(QUrl.fromLocalFile(self.temp_path))
        
        # Для хранения маркеров
        self.markers = []  # список маркеров для возможного удаления
    
    @Slot(float, float)
    def on_coords_received(self, lat, lon):
        """Обработка координат из JavaScript"""
        self.mapClicked.emit(lat, lon)
    
    def add_marker(self, lat, lon, text=""):
        """Добавляет постоянный маркер (красный)"""
        # Добавляем маркер через JavaScript
        js_code = f"""
        var marker = L.marker([{lat}, {lon}]).addTo(map);
        marker.bindPopup('{text}');
        """
        self.web_view.page().runJavaScript(js_code)
        self.markers.append({'lat': lat, 'lon': lon, 'text': text, 'temp': False})
        print(f"✓ Маркер добавлен: {lat}, {lon}")
    
    def add_temp_marker(self, lat, lon, text=""):
        """Добавляет временный маркер (синий) для предпросмотра"""
        print(f"Метод add_temp_marker ВЫЗВАН для {lat}, {lon}")
        
        # Добавляем временный маркер через JavaScript
        js_code = f"""
        // Удаляем предыдущий временный маркер если есть
        if (window.tempMarker) {{
            map.removeLayer(window.tempMarker);
        }}
        
        // Создаем новый временный маркер
        window.tempMarker = L.marker([{lat}, {lon}], {{
            icon: L.icon({{
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            }})
        }}).addTo(map);
        window.tempMarker.bindPopup('{text}');
        """
        self.web_view.page().runJavaScript(js_code)
        print(f"✓ Временный маркер добавлен: {lat}, {lon}")
    
    def clear_markers(self):
        """Очищает все маркеры"""
        js_code = """
        // Удаляем все маркеры
        map.eachLayer(function(layer) {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
        // Удаляем временный маркер
        window.tempMarker = null;
        """
        self.web_view.page().runJavaScript(js_code)
        self.markers = []
        print("✓ Все маркеры очищены")
    
    def reload(self):
        """Перезагружает карту"""
        self.web_view.reload()