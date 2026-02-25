#!/usr/bin/env python3
"""
Главный файл приложения Coastal Classifier
Запускает окно регистрации и затем главное окно с картой
"""

import sys
from PySide6.QtWidgets import QApplication

# Импортируем наше окно регистрации
from src.gui.registration_dialog import RegistrationDialog


def main():
    """Главная функция приложения"""
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("Coastal Classifier")
    app.setOrganizationName("CoastalResearch")
    
    # Показываем окно регистрации
    dialog = RegistrationDialog()
    
    # Если пользователь нажал "Начать работу"
    if dialog.exec() == RegistrationDialog.Accepted:
        # Получаем данные пользователя
        user_data = dialog.get_user_data()
        
        print("=" * 50)
        print("РЕГИСТРАЦИЯ УСПЕШНА")
        print("=" * 50)
        print(f"Пользователь: {user_data['first_name']} {user_data['last_name']}")
        print(f"Дата: {user_data['date']}")
        print(f"Файл для сохранения: {user_data['filename']}")
        print("=" * 50)
        
        # Здесь позже будет вызов главного окна
        print("Запуск главного окна приложения...")
        print("(будет добавлено на следующем шаге)")
        
        # TODO: Создать и показать главное окно с картой
        # from src.gui.main_window import MainWindow
        # window = MainWindow(user_data)
        # window.show()
        
        return 0  # Успешное завершение
    
    else:
        print("Регистрация отменена. Выход.")
        return 1  # Пользователь отменил


if __name__ == "__main__":
    sys.exit(main())