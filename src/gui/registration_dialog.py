"""
Окно регистрации пользователя с сохранением настроек
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, 
                               QMessageBox, QDateEdit, QComboBox)
from PySide6.QtCore import Qt, QDate
import sys
from pathlib import Path

# Добавляем импорты наших модулей
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config_manager import get_config_manager
from src.utils.i18n import get_i18n


class RegistrationDialog(QDialog):
    """Диалог регистрации с сохранением данных пользователя"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Загружаем менеджеры
        self.config = get_config_manager()
        self.i18n = get_i18n()
        
        # Настройки окна
        self.setWindowTitle(self.i18n.t('registration_title'))
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # Переменные для хранения данных
        self.user_data = {}
        
        # Словарь для хранения ссылок на изменяемые виджеты
        self.ui_labels = {}
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Загружаем сохраненные данные
        self.load_saved_data()
        
    def setup_ui(self):
        """Создание элементов интерфейса"""
        layout = QVBoxLayout()
        
        # ===== Выбор языка =====
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(self.i18n.t('language'))
        lang_layout.addWidget(self.lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        # Сохраняем ссылку
        self.ui_labels['language'] = self.lang_label
        
        layout.addLayout(lang_layout)
        layout.addSpacing(10)
        
        # ===== Поля ввода =====
        # Имя
        self.first_name_label = QLabel(self.i18n.t('first_name'))
        layout.addWidget(self.first_name_label)
        self.ui_labels['first_name'] = self.first_name_label
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText(self.i18n.t('first_name'))
        layout.addWidget(self.first_name_input)
        
        # Фамилия
        self.last_name_label = QLabel(self.i18n.t('last_name'))
        layout.addWidget(self.last_name_label)
        self.ui_labels['last_name'] = self.last_name_label
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText(self.i18n.t('last_name'))
        layout.addWidget(self.last_name_input)
        
        # Дата регистрации
        self.date_label = QLabel(self.i18n.t('registration_date'))
        layout.addWidget(self.date_label)
        self.ui_labels['registration_date'] = self.date_label
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_input)
        
        # ===== Предпросмотр имени файла =====
        self.filename_label = QLabel(self.i18n.t('filename_preview'))
        layout.addWidget(self.filename_label)
        self.ui_labels['filename_preview'] = self.filename_label
        
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.filename_preview)
        
        # ===== Кнопки =====
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton(self.i18n.t('start_button'))
        self.ok_button.clicked.connect(self.accept_registration)
        
        self.cancel_button = QPushButton(self.i18n.t('cancel'))
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Устанавливаем основной layout
        self.setLayout(layout)
        
        # Подключаем сигналы для обновления предпросмотра
        self.first_name_input.textChanged.connect(self.update_filename_preview)
        self.last_name_input.textChanged.connect(self.update_filename_preview)
        self.date_input.dateChanged.connect(self.update_filename_preview)
    
    def load_saved_data(self):
        """Загружает сохраненные данные пользователя"""
        saved_user = self.config.get_user_data()
        
        # Устанавливаем сохраненный язык
        current_lang = self.config.get_language()
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        # Заполняем поля, если есть сохраненные данные
        if saved_user.get('first_name'):
            self.first_name_input.setText(saved_user['first_name'])
        
        if saved_user.get('last_name'):
            self.last_name_input.setText(saved_user['last_name'])
        
        # Первоначальное обновление предпросмотра
        self.update_filename_preview()
    
    def on_language_changed(self, index):
        """Обработчик смены языка"""
        lang = self.lang_combo.itemData(index)
        if lang:
            self.i18n.set_language(lang)
            self.update_ui_language()
    
    def update_ui_language(self):
        """Обновляет все тексты интерфейса при смене языка"""
        # Обновляем заголовок окна
        self.setWindowTitle(self.i18n.t('registration_title'))
        
        # Обновляем все подписи из словаря
        for key, label in self.ui_labels.items():
            label.setText(self.i18n.t(key))
        
        # Обновляем плейсхолдеры
        self.first_name_input.setPlaceholderText(self.i18n.t('first_name'))
        self.last_name_input.setPlaceholderText(self.i18n.t('last_name'))
        
        # Обновляем текст кнопок
        self.ok_button.setText(self.i18n.t('start_button'))
        self.cancel_button.setText(self.i18n.t('cancel'))
        
        # Обновляем предпросмотр имени файла
        self.update_filename_preview()
    
    def update_filename_preview(self):
        """Обновляет предпросмотр имени файла"""
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        date = self.date_input.date().toString("yyyyMMdd")
        
        if first and last:
            # Формируем имя файла с учетом сессии
            session_num = self.config.get_user_data().get('sessions_count', 0) + 1
            filename = f"{last.upper()}_{first.capitalize()}_{date}_session{session_num:03d}.geojson"
            self.filename_preview.setText(filename)
            self.filename_preview.setStyleSheet("background-color: #e0ffe0; padding: 5px;")
        else:
            self.filename_preview.setText(self.i18n.t('filename_placeholder'))
            self.filename_preview.setStyleSheet("background-color: #ffe0e0; padding: 5px;")
    
    def accept_registration(self):
        """Обработка нажатия кнопки 'Начать работу'"""
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        
        # Валидация
        if not first:
            QMessageBox.warning(self, self.i18n.t('registration_title'), 
                              self.i18n.t('fill_name_warning'))
            return
        
        if not last:
            QMessageBox.warning(self, self.i18n.t('registration_title'), 
                              self.i18n.t('fill_lastname_warning'))
            return
        
        # Сохраняем данные пользователя в конфиг
        self.config.set_user_data(first, last)
        
        # Сохраняем данные для текущей сессии
        self.user_data = {
            'first_name': first,
            'last_name': last,
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'date_int': self.date_input.date().toString("yyyyMMdd"),
            'filename': self.filename_preview.text(),
            'session_number': self.config.get_user_data().get('sessions_count', 1)
        }
        
        # Закрываем диалог с успехом
        self.accept()
    
    def get_user_data(self):
        """Возвращает данные пользователя"""
        return self.user_data


# Для самостоятельного тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = RegistrationDialog()
    if dialog.exec() == QDialog.Accepted:
        data = dialog.get_user_data()
        print("\n" + "="*50)
        print("ДАННЫЕ ПОЛЬЗОВАТЕЛЯ")
        print("="*50)
        for key, value in data.items():
            print(f"{key}: {value}")
        
        # Показываем где сохранен конфиг
        config = get_config_manager()
        print(f"\nКонфигурация сохранена в: {config.config_file}")
    else:
        print("Регистрация отменена")
    
    sys.exit()