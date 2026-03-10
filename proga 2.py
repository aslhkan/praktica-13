import sys
import sqlite3
import os
import hashlib
import warnings
from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QTableWidgetItem, 
                             QMessageBox, QPushButton, QTableWidget, QLabel, 
                             QLineEdit, QComboBox, QSpinBox, QDialogButtonBox,
                             QHeaderView, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# Подавляем предупреждения sip
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ПАРОЛЯМИ ====================
def hash_password(password):
    """Хеширование пароля"""
    salt = "bd_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, hashed):
    """Проверка пароля"""
    return hash_password(password) == hashed

# ==================== ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ ====================
def get_db_connection():
    """Получение соединения с существующей БД bd"""
    try:
        db_path = r'bd'
        
        if not os.path.exists(db_path):
            QMessageBox.critical(None, 'Ошибка', 
                               f'Файл базы данных "bd" не найден!\n\n'
                               f'Убедитесь, что файл находится в папке:\n{os.path.abspath(".")}')
            return None
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    except Exception as e:
        QMessageBox.critical(None, 'Ошибка', f'Не удалось подключиться к БД: {str(e)}')
        return None

# ==================== ДИАЛОГ АВТОРИЗАЦИИ ====================
class LoginDialog(QDialog):
    """Диалог авторизации"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setModal(True)
        # Увеличиваем размер окна
        self.setMinimumSize(600, 450)
        self.resize(600, 450)
        
        # База данных пользователей
        self.users_db = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "full_name": "Администратор"
            },
            "user": {
                "password": hash_password("user123"),
                "role": "user",
                "full_name": "Обычный пользователь"
            },
            "manager": {
                "password": hash_password("manager123"),
                "role": "manager",
                "full_name": "Менеджер"
            }
        }
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#loginButton {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#loginButton:hover {
                background-color: #45a049;
            }
            QPushButton#cancelButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton#cancelButton:hover {
                background-color: #da190b;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # Заголовок
        title_label = QLabel("Вход в систему")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4CAF50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Поле для логина
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Логин")
        self.username_edit.setMinimumHeight(45)
        layout.addWidget(self.username_edit)
        
        # Поле для пароля
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(45)
        layout.addWidget(self.password_edit)
        
        layout.addStretch()
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginButton")
        self.login_button.setMinimumHeight(50)
        self.login_button.clicked.connect(self.check_credentials)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Информационная метка для ошибок
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #f44336; font-size: 13px; margin-top: 10px;")
        layout.addWidget(self.info_label)
        
        # Подсказка для входа
        hint_label = QLabel("Тестовые учетные записи:\nadmin / admin123\nuser / user123\nmanager / manager123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #666; font-size: 12px; background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-top: 20px;")
        layout.addWidget(hint_label)
        
        self.username_edit.setFocus()
        self.username_edit.returnPressed.connect(self.check_credentials)
        self.password_edit.returnPressed.connect(self.check_credentials)
    
    def check_credentials(self):
        """Проверка учетных данных"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.info_label.setText("Введите логин и пароль")
            return
        
        if username in self.users_db:
            if verify_password(password, self.users_db[username]["password"]):
                self.user_info = {
                    "username": username,
                    "role": self.users_db[username]["role"],
                    "full_name": self.users_db[username]["full_name"]
                }
                self.accept()
            else:
                self.info_label.setText("Неверный пароль")
                self.password_edit.clear()
                self.password_edit.setFocus()
        else:
            self.info_label.setText("Пользователь не найден")
            self.username_edit.clear()
            self.password_edit.clear()
            self.username_edit.setFocus()
    
    def get_user_info(self):
        """Получить информацию о пользователе"""
        return getattr(self, 'user_info', None)


# ==================== ДИАЛОГ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ ====================
class UserManagementDialog(QDialog):
    """Диалог управления пользователями"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление пользователями")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        
        self.users = {
            "admin": {
                "password": hash_password("admin123"),
                "role": "admin",
                "full_name": "Администратор"
            },
            "user": {
                "password": hash_password("user123"),
                "role": "user",
                "full_name": "Обычный пользователь"
            },
            "manager": {
                "password": hash_password("manager123"),
                "role": "manager",
                "full_name": "Менеджер"
            }
        }
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Управление пользователями")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4CAF50; margin: 10px;")
        layout.addWidget(title_label)
        
        # Таблица пользователей
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Логин", "Полное имя", "Роль", "Пароль (хеш)"])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.setAlternatingRowColors(True)
        layout.addWidget(self.user_table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_user)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.edit_button.clicked.connect(self.edit_user)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.delete_button.clicked.connect(self.delete_user)
        
        self.close_button = QPushButton("Закрыть")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.load_users()
    
    def load_users(self):
        """Загрузка списка пользователей"""
        self.user_table.setRowCount(len(self.users))
        
        row = 0
        for username, user_data in self.users.items():
            username_item = QTableWidgetItem(username)
            username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)
            self.user_table.setItem(row, 0, username_item)
            
            name_item = QTableWidgetItem(user_data["full_name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.user_table.setItem(row, 1, name_item)
            
            role_item = QTableWidgetItem(user_data["role"])
            role_item.setFlags(role_item.flags() & ~Qt.ItemIsEditable)
            self.user_table.setItem(row, 2, role_item)
            
            hash_item = QTableWidgetItem(user_data["password"][:20] + "...")
            hash_item.setFlags(hash_item.flags() & ~Qt.ItemIsEditable)
            hash_item.setToolTip(user_data["password"])
            self.user_table.setItem(row, 3, hash_item)
            
            row += 1
        
        self.user_table.resizeColumnsToContents()
    
    def add_user(self):
        """Добавление нового пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление пользователя")
        dialog.setModal(True)
        dialog.setFixedSize(400, 250)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        username_edit = QLineEdit()
        username_edit.setPlaceholderText("Введите логин")
        form_layout.addRow("Логин:", username_edit)
        
        fullname_edit = QLineEdit()
        fullname_edit.setPlaceholderText("Введите полное имя")
        form_layout.addRow("Полное имя:", fullname_edit)
        
        role_combo = QComboBox()
        role_combo.addItems(["user", "manager", "admin"])
        form_layout.addRow("Роль:", role_combo)
        
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("Введите пароль")
        password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", password_edit)
        
        confirm_edit = QLineEdit()
        confirm_edit.setPlaceholderText("Подтвердите пароль")
        confirm_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Подтверждение:", confirm_edit)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            username = username_edit.text().strip()
            fullname = fullname_edit.text().strip()
            role = role_combo.currentText()
            password = password_edit.text()
            confirm = confirm_edit.text()
            
            if not username:
                QMessageBox.warning(self, "Ошибка", "Введите логин")
                return
            
            if not fullname:
                QMessageBox.warning(self, "Ошибка", "Введите полное имя")
                return
            
            if username in self.users:
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                return
            
            if not password:
                QMessageBox.warning(self, "Ошибка", "Введите пароль")
                return
            
            if password != confirm:
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                return
            
            if len(password) < 6:
                QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
                return
            
            self.users[username] = {
                "password": hash_password(password),
                "role": role,
                "full_name": fullname
            }
            self.load_users()
            QMessageBox.information(self, "Успех", f"Пользователь {username} добавлен")
    
    def edit_user(self):
        """Редактирование пользователя"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для редактирования")
            return
        
        username = self.user_table.item(current_row, 0).text()
        
        if username == "admin":
            QMessageBox.warning(self, "Ошибка", "Нельзя редактировать администратора")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование пользователя {username}")
        dialog.setModal(True)
        dialog.setFixedSize(400, 250)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        fullname_edit = QLineEdit()
        fullname_edit.setText(self.users[username]["full_name"])
        form_layout.addRow("Полное имя:", fullname_edit)
        
        role_combo = QComboBox()
        role_combo.addItems(["user", "manager", "admin"])
        role_combo.setCurrentText(self.users[username]["role"])
        form_layout.addRow("Роль:", role_combo)
        
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("Оставьте пустым, если не хотите менять")
        password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Новый пароль:", password_edit)
        
        confirm_edit = QLineEdit()
        confirm_edit.setPlaceholderText("Подтвердите новый пароль")
        confirm_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Подтверждение:", confirm_edit)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            fullname = fullname_edit.text().strip()
            role = role_combo.currentText()
            password = password_edit.text()
            confirm = confirm_edit.text()
            
            if not fullname:
                QMessageBox.warning(self, "Ошибка", "Введите полное имя")
                return
            
            self.users[username]["full_name"] = fullname
            self.users[username]["role"] = role
            
            if password:
                if password != confirm:
                    QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                    return
                if len(password) < 6:
                    QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
                    return
                self.users[username]["password"] = hash_password(password)
            
            self.load_users()
            QMessageBox.information(self, "Успех", f"Пользователь {username} обновлен")
    
    def delete_user(self):
        """Удаление пользователя"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для удаления")
            return
        
        username = self.user_table.item(current_row, 0).text()
        
        if username == "admin":
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить администратора")
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить пользователя {username}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.users[username]
            self.load_users()
            QMessageBox.information(self, "Успех", f"Пользователь {username} удален")


# ==================== ИНТЕРФЕЙС ГЛАВНОГО ОКНА ====================
class MainInterface:
    """Интерфейс главного окна"""
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 750)
        Form.setWindowTitle("Управление заказами")
        
        central_widget = QWidget(Form)
        central_widget.setGeometry(20, 20, 960, 710)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_title = QLabel("Работа с базой данных bd")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(Qt.AlignCenter)
        
        user_panel = QWidget()
        user_layout = QVBoxLayout(user_panel)
        user_layout.setSpacing(2)
        
        self.user_label = QLabel("Пользователь: гость")
        self.user_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.user_label.setAlignment(Qt.AlignRight)
        
        self.logout_button = QPushButton("Выйти")
        self.logout_button.setMaximumWidth(80)
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        user_layout.addWidget(self.user_label)
        user_layout.addWidget(self.logout_button)
        
        top_layout.addWidget(self.label_title, 1)
        top_layout.addWidget(user_panel)
        
        main_layout.addWidget(top_panel)
        
        # Информация о БД
        self.label_db_info = QLabel("")
        self.label_db_info.setStyleSheet("color: #4CAF50; font-weight: bold;")
        main_layout.addWidget(self.label_db_info)
        
        # Панель выбора таблицы
        table_panel = QWidget()
        table_layout = QHBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 10, 0, 10)
        
        self.label_table = QLabel("Выберите таблицу:")
        self.label_table.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.combo_table = QComboBox()
        self.combo_table.setMinimumWidth(250)
        self.combo_table.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
        """)
        
        self.users_button = QPushButton("Пользователи")
        self.users_button.setMinimumHeight(35)
        self.users_button.setMaximumWidth(120)
        self.users_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        
        table_layout.addWidget(self.label_table)
        table_layout.addWidget(self.combo_table)
        table_layout.addStretch()
        table_layout.addWidget(self.users_button)
        
        main_layout.addWidget(table_panel)
        
        # Таблица данных
        self.tableWidget = QTableWidget()
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.tableWidget)
        
        # Панель кнопок
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)
        
        self.pushButton = QPushButton("Добавить запись")
        self.pushButton.setMinimumHeight(40)
        self.pushButton.setMinimumWidth(150)
        self.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.pushButton_edit = QPushButton("Редактировать")
        self.pushButton_edit.setMinimumHeight(40)
        self.pushButton_edit.setMinimumWidth(150)
        self.pushButton_edit.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        self.pushButton_delete = QPushButton("Удалить запись")
        self.pushButton_delete.setMinimumHeight(40)
        self.pushButton_delete.setMinimumWidth(150)
        self.pushButton_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.pushButton_refresh = QPushButton("Обновить")
        self.pushButton_refresh.setMinimumHeight(40)
        self.pushButton_refresh.setMinimumWidth(150)
        self.pushButton_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        
        button_layout.addWidget(self.pushButton)
        button_layout.addWidget(self.pushButton_edit)
        button_layout.addWidget(self.pushButton_delete)
        button_layout.addWidget(self.pushButton_refresh)
        button_layout.addStretch()
        
        main_layout.addWidget(button_panel)


# ==================== ДИАЛОГОВОЕ ОКНО (КЛИЕНТЫ) ====================
class ClientWindow(QDialog):
    """Класс окна добавления/редактирования клиента"""
    def __init__(self, parent=None, client_id=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setWindowTitle("Добавление клиента" if not client_id else "Редактирование клиента")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        group_box = QGroupBox("Данные клиента")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        form_layout = QVBoxLayout(group_box)
        
        surname_layout = QHBoxLayout()
        surname_layout.addWidget(QLabel("Фамилия:"))
        self.surname_edit = QLineEdit()
        self.surname_edit.setPlaceholderText("Введите фамилию")
        surname_layout.addWidget(self.surname_edit)
        form_layout.addLayout(surname_layout)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Имя:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя")
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        patronymic_layout = QHBoxLayout()
        patronymic_layout.addWidget(QLabel("Отчество:"))
        self.patronymic_edit = QLineEdit()
        self.patronymic_edit.setPlaceholderText("Введите отчество")
        patronymic_layout.addWidget(self.patronymic_edit)
        form_layout.addLayout(patronymic_layout)
        
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("Адрес:"))
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Введите адрес")
        address_layout.addWidget(self.address_edit)
        form_layout.addLayout(address_layout)
        
        layout.addWidget(group_box)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        button_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        button_box.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(button_box)
        
        if client_id:
            self.load_client_data()
    
    def load_client_data(self):
        """Загрузка данных клиента для редактирования"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT фамилия, имя, отчество, адрес FROM клиент WHERE rowid = ?', (self.client_id,))
                client = cursor.fetchone()
                conn.close()
                
                if client:
                    self.surname_edit.setText(client[0] or '')
                    self.name_edit.setText(client[1] or '')
                    self.patronymic_edit.setText(client[2] or '')
                    self.address_edit.setText(client[3] or '')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')
    
    def get_client_data(self):
        return (self.surname_edit.text().strip(), 
                self.name_edit.text().strip(), 
                self.patronymic_edit.text().strip(),
                self.address_edit.text().strip())
    
    def accept(self):
        surname, name, patronymic, address = self.get_client_data()
        
        if not surname or not name:
            QMessageBox.warning(self, 'Предупреждение', 'Введите фамилию и имя клиента')
            return
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                if self.client_id:
                    cursor.execute('''
                        UPDATE клиент 
                        SET фамилия=?, имя=?, отчество=?, адрес=?
                        WHERE rowid=?
                    ''', (surname, name, patronymic, address, self.client_id))
                else:
                    cursor.execute('''
                        INSERT INTO клиент (фамилия, имя, отчество, адрес)
                        VALUES (?, ?, ?, ?)
                    ''', (surname, name, patronymic, address))
                
                conn.commit()
                conn.close()
                super().accept()
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить данные: {str(e)}')


# ==================== ДИАЛОГОВОЕ ОКНО (КВАРТИРЫ) ====================
class ApartmentWindow(QDialog):
    """Класс окна добавления/редактирования квартиры"""
    def __init__(self, parent=None, apartment_id=None):
        super().__init__(parent)
        self.apartment_id = apartment_id
        self.setWindowTitle("Добавление квартиры" if not apartment_id else "Редактирование квартиры")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        group_box = QGroupBox("Данные квартиры")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        form_layout = QVBoxLayout(group_box)
        
        city_layout = QHBoxLayout()
        city_layout.addWidget(QLabel("Город:"))
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Введите город")
        city_layout.addWidget(self.city_edit)
        form_layout.addLayout(city_layout)
        
        district_layout = QHBoxLayout()
        district_layout.addWidget(QLabel("Район:"))
        self.district_edit = QLineEdit()
        self.district_edit.setPlaceholderText("Введите район")
        district_layout.addWidget(self.district_edit)
        form_layout.addLayout(district_layout)
        
        rooms_layout = QHBoxLayout()
        rooms_layout.addWidget(QLabel("Количество комнат:"))
        self.rooms_spin = QSpinBox()
        self.rooms_spin.setRange(1, 10)
        self.rooms_spin.setValue(2)
        rooms_layout.addWidget(self.rooms_spin)
        form_layout.addLayout(rooms_layout)
        
        floor_layout = QHBoxLayout()
        floor_layout.addWidget(QLabel("Этаж:"))
        self.floor_spin = QSpinBox()
        self.floor_spin.setRange(1, 50)
        self.floor_spin.setValue(5)
        floor_layout.addWidget(self.floor_spin)
        form_layout.addLayout(floor_layout)
        
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Телефон:"))
        self.phone_combo = QComboBox()
        self.phone_combo.addItems(["нет", "да"])
        phone_layout.addWidget(self.phone_combo)
        form_layout.addLayout(phone_layout)
        
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("Код квартиры:"))
        self.code_spin = QSpinBox()
        self.code_spin.setRange(1, 999999)
        code_layout.addWidget(self.code_spin)
        form_layout.addLayout(code_layout)
        
        layout.addWidget(group_box)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        button_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        button_box.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(button_box)
        
        if apartment_id:
            self.load_apartment_data()
    
    def load_apartment_data(self):
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT "код квартиры", город, район, "количество комнат", этаж, телефон FROM квартиры WHERE rowid = ?', (self.apartment_id,))
                apartment = cursor.fetchone()
                conn.close()
                
                if apartment:
                    self.code_spin.setValue(apartment[0] or 0)
                    self.city_edit.setText(apartment[1] or '')
                    self.district_edit.setText(apartment[2] or '')
                    self.rooms_spin.setValue(apartment[3] or 2)
                    self.floor_spin.setValue(apartment[4] or 5)
                    index = self.phone_combo.findText(apartment[5] or 'нет')
                    if index >= 0:
                        self.phone_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')
    
    def get_apartment_data(self):
        return (self.code_spin.value(),
                self.city_edit.text().strip(), 
                self.district_edit.text().strip(),
                self.rooms_spin.value(),
                self.floor_spin.value(),
                self.phone_combo.currentText())
    
    def accept(self):
        code, city, district, rooms, floor, phone = self.get_apartment_data()
        
        if not city or not district:
            QMessageBox.warning(self, 'Предупреждение', 'Введите город и район')
            return
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                if self.apartment_id:
                    cursor.execute('''
                        UPDATE квартиры 
                        SET "код квартиры"=?, город=?, район=?, "количество комнат"=?, этаж=?, телефон=?
                        WHERE rowid=?
                    ''', (code, city, district, rooms, floor, phone, self.apartment_id))
                else:
                    cursor.execute('''
                        INSERT INTO квартиры ("код квартиры", город, район, "количество комнат", этаж, телефон)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (code, city, district, rooms, floor, phone))
                
                conn.commit()
                conn.close()
                super().accept()
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить данные: {str(e)}')


# ==================== ДИАЛОГОВОЕ ОКНО (ЗАКАЗЫ) ====================
class OrderWindow(QDialog):
    """Класс окна добавления/редактирования заказа"""
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle("Добавление заказа" if not order_id else "Редактирование заказа")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        group_box = QGroupBox("Данные заказа")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        form_layout = QVBoxLayout(group_box)
        
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("ID заказа:"))
        self.id_spin = QSpinBox()
        self.id_spin.setRange(1, 999999)
        id_layout.addWidget(self.id_spin)
        form_layout.addLayout(id_layout)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата заказа:"))
        self.date_spin = QSpinBox()
        self.date_spin.setRange(20200101, 20301231)
        self.date_spin.setValue(int(QDate.currentDate().toString("yyyyMMdd")))
        self.date_spin.setSuffix(" (ГГГГММДД)")
        date_layout.addWidget(self.date_spin)
        form_layout.addLayout(date_layout)
        
        urgency_layout = QHBoxLayout()
        urgency_layout.addWidget(QLabel("Срочность:"))
        self.urgency_spin = QSpinBox()
        self.urgency_spin.setRange(1, 3)
        self.urgency_spin.setValue(1)
        urgency_layout.addWidget(self.urgency_spin)
        form_layout.addLayout(urgency_layout)
        
        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Стоимость:"))
        self.cost_spin = QSpinBox()
        self.cost_spin.setRange(0, 100000000)
        self.cost_spin.setSingleStep(1000)
        self.cost_spin.setValue(5000)
        cost_layout.addWidget(self.cost_spin)
        form_layout.addLayout(cost_layout)
        
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Скидка (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setValue(0)
        discount_layout.addWidget(self.discount_spin)
        form_layout.addLayout(discount_layout)
        
        layout.addWidget(group_box)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        button_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        button_box.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(button_box)
        
        if order_id:
            self.load_order_data()
    
    def load_order_data(self):
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT "id заказа", "дата заказа", срочность, стоймость, скидка FROM закакз WHERE rowid = ?', (self.order_id,))
                order = cursor.fetchone()
                conn.close()
                
                if order:
                    self.id_spin.setValue(order[0] or 0)
                    self.date_spin.setValue(order[1] or int(QDate.currentDate().toString("yyyyMMdd")))
                    self.urgency_spin.setValue(order[2] or 1)
                    self.cost_spin.setValue(order[3] or 0)
                    self.discount_spin.setValue(order[4] or 0)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')
    
    def get_order_data(self):
        return (self.id_spin.value(),
                self.date_spin.value(),
                self.urgency_spin.value(),
                self.cost_spin.value(),
                self.discount_spin.value())
    
    def accept(self):
        order_id, date, urgency, cost, discount = self.get_order_data()
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                if self.order_id:
                    cursor.execute('''
                        UPDATE закакз 
                        SET "id заказа"=?, "дата заказа"=?, срочность=?, стоймость=?, скидка=?
                        WHERE rowid=?
                    ''', (order_id, date, urgency, cost, discount, self.order_id))
                else:
                    cursor.execute('''
                        INSERT INTO закакз ("id заказа", "дата заказа", срочность, стоймость, скидка)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (order_id, date, urgency, cost, discount))
                
                conn.commit()
                conn.close()
                super().accept()
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить данные: {str(e)}')


# ==================== ГЛАВНОЕ ОКНО ====================
class MainWindow(QWidget):
    """Главное окно программы"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = MainInterface()
        self.ui.setupUi(self)
        
        self.current_user = None
        self.current_table = None
        
        self.ui.pushButton.clicked.connect(self.add_record)
        self.ui.pushButton_edit.clicked.connect(self.edit_record)
        self.ui.pushButton_delete.clicked.connect(self.delete_record)
        self.ui.pushButton_refresh.clicked.connect(self.load_data)
        self.ui.combo_table.currentIndexChanged.connect(self.change_table)
        self.ui.tableWidget.doubleClicked.connect(self.edit_record)
        self.ui.logout_button.clicked.connect(self.logout)
        self.ui.users_button.clicked.connect(self.manage_users)
        
        self.show_login()
    
    def show_login(self):
        """Показ окна авторизации"""
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            user_info = login_dialog.get_user_info()
            if user_info:
                self.current_user = user_info["username"]
                self.ui.user_label.setText(f"Пользователь: {user_info['full_name']} ({user_info['role']})")
                
                if self.current_user == "admin":
                    self.ui.users_button.show()
                else:
                    self.ui.users_button.hide()
                
                self.load_table_list()
                
                if self.ui.combo_table.count() > 0 and self.ui.combo_table.currentText() != "Нет таблиц с данными":
                    self.change_table(0)
        else:
            sys.exit()
    
    def logout(self):
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что хотите выйти из системы?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.ui.user_label.setText("Пользователь: гость")
            self.ui.combo_table.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0)
            self.show_login()
    
    def manage_users(self):
        if self.current_user == "admin":
            dialog = UserManagementDialog(self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Доступ запрещен", "Только администратор может управлять пользователями")
    
    def load_table_list(self):
        """Загрузка списка таблиц из базы данных (только непустые)"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                self.ui.combo_table.clear()
                non_empty_tables = []
                
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                        count = cursor.fetchone()[0]
                        
                        if count > 0:
                            non_empty_tables.append(table_name)
                            self.ui.combo_table.addItem(table_name)
                    except Exception as e:
                        print(f"Ошибка при проверке таблицы {table_name}: {e}")
                        non_empty_tables.append(table_name)
                        self.ui.combo_table.addItem(table_name)
                
                conn.close()
                
                db_path = os.path.abspath('bd')
                self.ui.label_db_info.setText(
                    f"База данных: {db_path}\n"
                    f"Всего таблиц: {len(tables)}\n"
                    f"Таблиц с данными: {len(non_empty_tables)}"
                )
                
                if len(non_empty_tables) == 0:
                    self.ui.label_db_info.setText(
                        f"База данных: {db_path}\n"
                        f"Все таблицы пусты!"
                    )
                    self.ui.combo_table.addItem("Нет таблиц с данными")
                    self.ui.combo_table.setEnabled(False)
                    self.ui.pushButton.setEnabled(False)
                    self.ui.pushButton_edit.setEnabled(False)
                    self.ui.pushButton_delete.setEnabled(False)
                else:
                    self.ui.combo_table.setEnabled(True)
                    self.ui.pushButton.setEnabled(True)
                    self.ui.pushButton_edit.setEnabled(True)
                    self.ui.pushButton_delete.setEnabled(True)
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить список таблиц: {str(e)}')
    
    def change_table(self, index):
        if index >= 0 and self.ui.combo_table.currentText() != "Нет таблиц с данными":
            self.current_table = self.ui.combo_table.currentText()
            self.ui.label_title.setText(f"Таблица: {self.current_table}")
            self.load_data()
    
    def load_data(self):
        if not self.current_table:
            return
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                cursor.execute(f'SELECT rowid, * FROM "{self.current_table}"')
                data = cursor.fetchall()
                
                cursor.execute(f'PRAGMA table_info("{self.current_table}")')
                columns = cursor.fetchall()
                column_names = ['ID'] + [col[1] for col in columns]
                
                conn.close()
                
                self.ui.tableWidget.setRowCount(len(data))
                self.ui.tableWidget.setColumnCount(len(column_names))
                self.ui.tableWidget.setHorizontalHeaderLabels(column_names)
                
                for row, record in enumerate(data):
                    for col, value in enumerate(record):
                        item = QTableWidgetItem(str(value) if value is not None else "")
                        item.setData(Qt.UserRole, record[0])
                        item.setTextAlignment(Qt.AlignCenter)
                        self.ui.tableWidget.setItem(row, col, item)
                
                self.ui.tableWidget.resizeColumnsToContents()
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить данные: {str(e)}')
    
    def add_record(self):
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Выберите таблицу")
            return
        
        if self.current_table == "клиент":
            dialog = ClientWindow(self)
        elif self.current_table == "квартиры":
            dialog = ApartmentWindow(self)
        elif self.current_table == "закакз":
            dialog = OrderWindow(self)
        else:
            QMessageBox.information(self, "Информация", 
                                  f"Редактирование таблицы '{self.current_table}' не реализовано")
            return
        
        if dialog.exec_():
            self.load_data()
            self.load_table_list()
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
    
    def edit_record(self):
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Выберите таблицу")
            return
        
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
            return
        
        record_id = self.ui.tableWidget.item(current_row, 0).data(Qt.UserRole)
        
        if self.current_table == "клиент":
            dialog = ClientWindow(self, record_id)
        elif self.current_table == "квартиры":
            dialog = ApartmentWindow(self, record_id)
        elif self.current_table == "закакз":
            dialog = OrderWindow(self, record_id)
        else:
            QMessageBox.information(self, "Информация", 
                                  f"Редактирование таблицы '{self.current_table}' не реализовано")
            return
        
        if dialog.exec_():
            self.load_data()
            QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
    
    def delete_record(self):
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Выберите таблицу")
            return
        
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
            return
        
        record_id = self.ui.tableWidget.item(current_row, 0).data(Qt.UserRole)
        
        record_info = ""
        for col in range(1, min(3, self.ui.tableWidget.columnCount())):
            item = self.ui.tableWidget.item(current_row, col)
            if item and item.text():
                record_info += item.text() + " "
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить запись?\n\n{record_info}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    cursor.execute(f'DELETE FROM "{self.current_table}" WHERE rowid = ?', (record_id,))
                    conn.commit()
                    conn.close()
                    
                    self.load_data()
                    self.load_table_list()
                    QMessageBox.information(self, "Успех", "Запись успешно удалена!")
                    
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить запись: {str(e)}')


# ==================== ТОЧКА ВХОДА ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    if not os.path.exists('bd'):
        QMessageBox.critical(None, 'Ошибка', 
                           'Файл базы данных "bd" не найден!\n\n'
                           'Пожалуйста, убедитесь, что файл находится в папке:\n'
                           f'{os.path.abspath(".")}')
        return
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
