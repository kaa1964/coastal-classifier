"""
Окно регистрации пользователя
Собирает имя, фамилию и генерирует имя файла для сохранения результатов
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, 
                               QMessageBox, QDateEdit)
from PySide6.QtCore import Qt, QDate
import datetime

class RegistrationDialog(QDialog):
    """Диалог регистрации нового пользователя"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Настройки окна
        self.setWindowTitle("Регистрация пользователя")
        self.setModal(True)  # Модальное окно (блокирует родительское)
        self.setMinimumWidth(400)
        
        # Переменные для хранения данных
        self.user_data = {}
        
        # Создаем интерфейс
        self.setup_ui()
        
    def setup_ui(self):
        """Создание элементов интерфейса"""
        layout = QVBoxLayout()
        
        # ===== Поля ввода =====
        # Имя
        layout.addWidget(QLabel("Имя:"))
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Введите ваше имя")
        layout.addWidget(self.first_name_input)
        
        # Фамилия
        layout.addWidget(QLabel("Фамилия:"))
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Введите вашу фамилию")
        layout.addWidget(self.last_name_input)
        
        # Дата регистрации (автоматически текущая)
        layout.addWidget(QLabel("Дата регистрации:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.date_input)
        
        # ===== Предпросмотр имени файла =====
        layout.addWidget(QLabel("Имя файла для сохранения:"))
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.filename_preview)
        
        # ===== Кнопки =====
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Начать работу")
        self.ok_button.clicked.connect(self.accept_registration)
        
        self.cancel_button = QPushButton("Отмена")
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
        
        # Первоначальное обновление
        self.update_filename_preview()
    
    def update_filename_preview(self):
        """Обновляет предпросмотр имени файла"""
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        date = self.date_input.date().toString("yyyyMMdd")
        
        if first and last:
            # Формируем имя файла: ФАМИЛИЯ_Имя_ГГГГММДД.geojson
            filename = f"{last.upper()}_{first.capitalize()}_{date}.geojson"
            self.filename_preview.setText(filename)
            self.filename_preview.setStyleSheet("background-color: #e0ffe0; padding: 5px;")
        else:
            self.filename_preview.setText("Заполните имя и фамилию")
            self.filename_preview.setStyleSheet("background-color: #ffe0e0; padding: 5px;")
    
    def accept_registration(self):
        """Обработка нажатия кнопки 'Начать работу'"""
        first = self.first_name_input.text().strip()
        last = self.last_name_input.text().strip()
        
        # Валидация
        if not first:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите имя")
            return
        
        if not last:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите фамилию")
            return
        
        # Сохраняем данные пользователя
        self.user_data = {
            'first_name': first,
            'last_name': last,
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'date_int': self.date_input.date().toString("yyyyMMdd"),
            'filename': self.filename_preview.text()
        }
        
        # Закрываем диалог с успехом
        self.accept()
    
    def get_user_data(self):
        """Возвращает данные пользователя"""
        return self.user_data


# Для самостоятельного тестирования
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = RegistrationDialog()
    if dialog.exec() == QDialog.Accepted:
        data = dialog.get_user_data()
        print("Данные пользователя:")
        print(f"Имя: {data['first_name']}")
        print(f"Фамилия: {data['last_name']}")
        print(f"Дата: {data['date']}")
        print(f"Файл: {data['filename']}")
    else:
        print("Регистрация отменена")
    
    sys.exit()