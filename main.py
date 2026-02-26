#!/usr/bin/env python3
"""
Главный файл приложения Coastal Classifier
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from src.gui.registration_dialog import RegistrationDialog
from src.gui.main_window import MainWindow  # Добавлен импорт
from src.utils.config_manager import get_config_manager
from src.utils.i18n import get_i18n


def main():
    """Главная функция приложения"""
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("Coastal Classifier")
    app.setOrganizationName("CoastalResearch")
    
    # Загружаем конфигурацию
    config = get_config_manager()
    i18n = get_i18n()
    
    print("=" * 50)
    print("Coastal Classifier")
    print("=" * 50)
    print(f"Конфигурация: {config.config_file}")
    print(f"Язык интерфейса: {config.get_language()}")
    print("=" * 50)
    
    # Показываем окно регистрации
    dialog = RegistrationDialog()
    
    # Если пользователь нажал "Начать работу"
    if dialog.exec() == RegistrationDialog.Accepted:
        user_data = dialog.get_user_data()
        
        print("\n" + "=" * 50)
        print("РЕГИСТРАЦИЯ УСПЕШНА")
        print("=" * 50)
        print(f"Пользователь: {user_data['first_name']} {user_data['last_name']}")
        print(f"Сессия: {user_data['session_number']}")
        print(f"Файл: {user_data['filename']}")
        print("=" * 50)
        
        # Создаем и показываем главное окно
        window = MainWindow(user_data)
        window.show()
        
        return app.exec()
    
    else:
        print("\nРегистрация отменена. Выход.")
        return 1


if __name__ == "__main__":
    sys.exit(main())