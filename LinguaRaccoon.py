import sys
import json
import os
import random
import re
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStackedWidget,
    QFrame, QScrollArea, QGridLayout, QProgressBar,
    QMessageBox, QLineEdit, QComboBox, QRadioButton, QButtonGroup,
    QDialog, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import Qt, QMimeData, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QDrag, QPixmap, QColor, QPainter, QPainterPath, QPen, QBrush


class RepeatLessonDialog(QDialog):
    """Диалог подтверждения повторения урока"""

    def __init__(self, lesson_title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Повторение урока")
        self.setModal(True)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        question_label = QLabel(f"Вы уже прошли урок\n\"{lesson_title}\"\n\nХотите повторить его?")
        question_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setWordWrap(True)
        question_label.setStyleSheet("color: black;")
        layout.addWidget(question_label)

        layout.addSpacing(30)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.yes_btn = QPushButton("✅ ДА")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.clicked.connect(self.accept)

        self.no_btn = QPushButton("❌ НЕТ")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.yes_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.no_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class ExitConfirmationDialog(QDialog):
    """Диалог подтверждения выхода из аккаунта"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подтверждение выхода")
        self.setModal(True)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        question_label = QLabel("Вы уверены, что хотите выйти из аккаунта?")
        question_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setStyleSheet("color: black;")
        layout.addWidget(question_label)

        layout.addSpacing(30)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.yes_btn = QPushButton("ДА")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.clicked.connect(self.accept)

        self.no_btn = QPushButton("НЕТ")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.yes_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.no_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)


class DraggableWord(QLabel):
    """Перетаскиваемое слово для задания на составление предложения"""

    def __init__(self, text, parent=None, is_in_dropzone=False, on_remove=None, on_return=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 14))
        self.setCursor(Qt.PointingHandCursor)
        self.is_in_dropzone = is_in_dropzone
        self.on_remove = on_remove
        self.on_return = on_return
        self.update_style()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(100)
        self.setMinimumHeight(50)

    def update_style(self):
        if self.is_in_dropzone:
            self.setStyleSheet("""
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    padding: 8px;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QLabel:hover {
                    background-color: #1976D2;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    border: 2px solid #45a049;
                    font-weight: bold;
                }
                QLabel:hover {
                    background-color: #45a049;
                }
            """)

    def set_correct_style(self):
        self.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid #2E7D32;
            }
        """)

    def set_wrong_style(self):
        self.setStyleSheet("""
            QLabel {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid #c62828;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            mime_data.setData("text/plain", self.text().encode())
            drag.setMimeData(mime_data)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec_(Qt.MoveAction)

    def mouseDoubleClickEvent(self, event):
        if self.is_in_dropzone and self.on_return:
            self.on_return(self)


class ImprovedDropZone(QFrame):
    """Улучшенная зона для сборки предложения с возможностью возврата слов"""

    def __init__(self, parent=None, on_word_removed=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.words = []
        self.word_widgets = []
        self.on_word_removed = on_word_removed
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px dashed #4CAF50;
                border-radius: 15px;
                min-height: 100px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        word = event.mimeData().text()
        source = event.source()
        if source and hasattr(source, 'on_remove'):
            source.on_remove(source)
        self.add_word(word)
        event.acceptProposedAction()

    def add_word(self, word):
        word_label = DraggableWord(word, self, is_in_dropzone=True, on_return=self.return_word)
        word_label.mousePressEvent = lambda e: self.remove_word_by_click(word_label)
        word_label.mouseDoubleClickEvent = lambda e: self.return_word(word_label)
        word_label.setCursor(Qt.PointingHandCursor)
        self.words.append(word)
        self.word_widgets.append(word_label)
        self.layout.addWidget(word_label)

    def remove_word_by_click(self, word_label):
        if word_label in self.word_widgets:
            index = self.word_widgets.index(word_label)
            word_text = self.words[index]
            self.words.pop(index)
            self.word_widgets.pop(index)
            word_label.deleteLater()
            if self.on_word_removed:
                self.on_word_removed(word_text, from_dropzone=True)

    def return_word(self, word_widget):
        if word_widget in self.word_widgets:
            index = self.word_widgets.index(word_widget)
            word_text = self.words[index]
            self.words.pop(index)
            self.word_widgets.pop(index)
            word_widget.deleteLater()
            if self.on_word_removed:
                self.on_word_removed(word_text, from_dropzone=True)

    def get_sentence(self):
        return " ".join(self.words)

    def clear_words(self):
        for widget in self.word_widgets:
            widget.deleteLater()
        self.words = []
        self.word_widgets = []

    def highlight_correct(self):
        for widget in self.word_widgets:
            widget.set_correct_style()

    def highlight_wrong(self):
        for widget in self.word_widgets:
            widget.set_wrong_style()


class WordBankWidget(QWidget):
    """Виджет с банком слов для перетаскивания (слова исчезают при перетаскивании)"""

    def __init__(self, words, on_word_removed=None, parent=None):
        super().__init__(parent)
        self.words = words
        self.word_widgets = []
        self.on_word_removed = on_word_removed
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.update_words()

    def update_words(self):
        for widget in self.word_widgets:
            widget.deleteLater()
        self.word_widgets = []

        for word in self.words:
            word_label = DraggableWord(word, self, is_in_dropzone=False, on_remove=self.remove_word)
            self.word_widgets.append(word_label)
            self.layout.addWidget(word_label)

    def remove_word(self, word_widget):
        if word_widget in self.word_widgets:
            index = self.word_widgets.index(word_widget)
            word_text = self.words[index]
            self.words.pop(index)
            self.word_widgets.pop(index)
            word_widget.deleteLater()
            if self.on_word_removed:
                self.on_word_removed(word_text, from_dropzone=False)

    def add_word(self, word_text):
        self.words.append(word_text)
        word_label = DraggableWord(word_text, self, is_in_dropzone=False, on_remove=self.remove_word)
        self.word_widgets.append(word_label)
        self.layout.addWidget(word_label)


class TranslationTask(QWidget):
    """Задание на перевод (вписать слово полностью)"""

    def __init__(self, task_data, on_complete, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.on_complete = on_complete
        self.is_answered = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        question_label = QLabel(f"📝 Переведите слово:\n{self.task_data['question']}")
        question_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setWordWrap(True)
        layout.addWidget(question_label)

        layout.addSpacing(30)

        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Введите перевод слова...")
        self.answer_input.setMinimumWidth(400)
        self.answer_input.setFont(QFont("Segoe UI", 14))
        self.answer_input.returnPressed.connect(self.check_answer)
        input_layout.addWidget(self.answer_input)

        layout.addLayout(input_layout)

        layout.addSpacing(30)

        button_layout = QHBoxLayout()
        self.check_btn = QPushButton("✅ Проверить")
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.clicked.connect(self.check_answer)
        button_layout.addWidget(self.check_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_answer(self):
        if self.is_answered:
            return
        user_answer = self.answer_input.text().strip().lower()
        correct_answer = self.task_data['correct'].lower()

        if user_answer == correct_answer:
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(True)
        else:
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(False)


class LanguageSelectionPage(QWidget):
    """Страница выбора языка"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        back_btn = QPushButton("← Назад")
        back_btn.setMaximumWidth(100)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        layout.addSpacing(50)

        title = QLabel("🌍 Выберите язык для изучения")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Какой язык вы хотите изучать?")
        subtitle.setFont(QFont("Segoe UI", 16))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(50)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        english_btn = QPushButton("🇬🇧 Английский\nEnglish")
        english_btn.setFont(QFont("Segoe UI", 18, QFont.Bold))
        english_btn.setMinimumHeight(150)
        english_btn.setMinimumWidth(250)
        english_btn.setCursor(Qt.PointingHandCursor)
        english_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        english_btn.clicked.connect(lambda: self.select_language("english"))
        button_layout.addWidget(english_btn)

        german_btn = QPushButton("🇩🇪 Немецкий\nDeutsch")
        german_btn.setFont(QFont("Segoe UI", 18, QFont.Bold))
        german_btn.setMinimumHeight(150)
        german_btn.setMinimumWidth(250)
        german_btn.setCursor(Qt.PointingHandCursor)
        german_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 15px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        german_btn.clicked.connect(lambda: self.select_language("german"))
        button_layout.addWidget(german_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_language(self, language):
        self.parent.current_language = language
        self.parent.db.set_preferred_language(self.parent.current_user_email, language)
        self.parent.switch_to_main()

    def go_back(self):
        self.parent.switch_to_main()


class UserDatabase:
    """Класс для работы с базой данных пользователей"""

    def __init__(self):
        self.users_file = "users_data.json"
        self.current_session_file = "current_session.json"
        self.load_users()
        self.load_current_session()

    def load_current_session(self):
        if os.path.exists(self.current_session_file):
            try:
                with open(self.current_session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_session = data.get('current_user', None)
            except:
                self.current_session = None
        else:
            self.current_session = None

    def save_current_session(self, email):
        try:
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump({'current_user': email}, f, ensure_ascii=False, indent=2)
        except:
            pass

    def clear_current_session(self):
        try:
            if os.path.exists(self.current_session_file):
                os.remove(self.current_session_file)
            self.current_session = None
        except:
            pass

    def reset_user_data(self, user_data):
        return {
            'name': user_data.get('name', ''),
            'password': user_data.get('password', ''),
            'join_date': user_data.get('join_date', datetime.now().isoformat()),
            'last_login': user_data.get('last_login', datetime.now().isoformat()),
            'preferred_language': user_data.get('preferred_language', 'english'),
            'unlocked_lessons': user_data.get('unlocked_lessons', {'english': [1], 'german': [1]}),
            'completed_lessons': user_data.get('completed_lessons', {'english': {}, 'german': {}}),
            'language_xp': user_data.get('language_xp', {'english': 0, 'german': 0}),
            'language_level': user_data.get('language_level', {'english': 1, 'german': 1}),
            'lesson_repeat_count': user_data.get('lesson_repeat_count', {}),
            'streak_days': user_data.get('streak_days', 0),
            'last_streak_date': user_data.get('last_streak_date', None)
        }

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    old_users = data.get('users', {})
                    self.users = {}
                    for email, user_data in old_users.items():
                        self.users[email] = self.reset_user_data(user_data)
                    self.save_users()
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                self.users = {}
        else:
            self.users = {}

    def save_users(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({'users': self.users}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def register_user(self, email, name, password):
        if email in self.users:
            return False, "Пользователь с таким email уже существует"

        now = datetime.now()
        self.users[email] = {
            'name': name,
            'password': password,
            'join_date': now.isoformat(),
            'last_login': now.isoformat(),
            'preferred_language': 'english',
            'unlocked_lessons': {'english': [1], 'german': [1]},
            'completed_lessons': {'english': {}, 'german': {}},
            'language_xp': {'english': 0, 'german': 0},
            'language_level': {'english': 1, 'german': 1},
            'lesson_repeat_count': {},
            'streak_days': 0,
            'last_streak_date': None
        }
        self.save_users()
        return True, self.users[email]

    def set_preferred_language(self, email, language):
        if email in self.users:
            self.users[email]['preferred_language'] = language
            self.save_users()

    def login_user(self, email, password):
        if email not in self.users:
            return False, "Пользователь не найден"

        if self.users[email]['password'] != password:
            return False, "Неверный пароль"

        now = datetime.now()
        last_login_str = self.users[email].get('last_login')

        if last_login_str:
            try:
                last_login = datetime.fromisoformat(last_login_str)
                days_diff = (now.date() - last_login.date()).days

                if days_diff > 1:
                    self.users[email]['streak_days'] = 0
                    self.users[email]['last_streak_date'] = None
            except:
                pass

        self.users[email]['last_login'] = now.isoformat()
        self.save_users()
        self.save_current_session(email)

        return True, self.users[email]

    def update_streak(self, email):
        if email in self.users:
            now = datetime.now()
            last_streak_date = self.users[email].get('last_streak_date')

            if last_streak_date is None:
                self.users[email]['streak_days'] = 1
                self.users[email]['last_streak_date'] = now.isoformat()
            else:
                try:
                    last_date = datetime.fromisoformat(last_streak_date)
                    days_diff = (now.date() - last_date.date()).days

                    if days_diff == 1:
                        self.users[email]['streak_days'] += 1
                        self.users[email]['last_streak_date'] = now.isoformat()
                    elif days_diff == 0:
                        pass
                    else:
                        self.users[email]['streak_days'] = 1
                        self.users[email]['last_streak_date'] = now.isoformat()
                except:
                    self.users[email]['streak_days'] = 1
                    self.users[email]['last_streak_date'] = now.isoformat()

            self.save_users()

    def logout(self):
        self.clear_current_session()

    def unlock_next_lesson(self, email, language, current_lesson_id):
        if email in self.users:
            next_lesson = current_lesson_id + 1
            unlocked = self.users[email]['unlocked_lessons'][language]
            if next_lesson not in unlocked:
                unlocked.append(next_lesson)
                unlocked.sort()
                self.save_users()
                return True
        return False

    def add_language_xp(self, email, language, xp):
        if email in self.users:
            self.users[email]['language_xp'][language] += xp
            new_level = 1 + (self.users[email]['language_xp'][language] // 100)
            self.users[email]['language_level'][language] = new_level
            self.save_users()

    def get_lesson_repeat_count(self, email, language, lesson_id):
        if email in self.users:
            key = f"{language}_{lesson_id}"
            return self.users[email]['lesson_repeat_count'].get(key, 0)
        return 0

    def complete_lesson(self, email, language, lesson_id):
        if email in self.users:
            key = str(lesson_id)
            repeat_count = self.get_lesson_repeat_count(email, language, lesson_id)

            if repeat_count == 0:
                xp_reward = 50
            else:
                xp_reward = 20

            if key not in self.users[email]['completed_lessons'][language]:
                self.users[email]['completed_lessons'][language][key] = {
                    'date': datetime.now().isoformat(),
                    'completed': True
                }
                self.add_language_xp(email, language, xp_reward)
                self.update_streak(email)

            lesson_key = f"{language}_{lesson_id}"
            if lesson_key not in self.users[email]['lesson_repeat_count']:
                self.users[email]['lesson_repeat_count'][lesson_key] = 1
            else:
                self.users[email]['lesson_repeat_count'][lesson_key] += 1

            self.save_users()
            return True, xp_reward
        return False, 0

    def is_lesson_completed(self, email, language, lesson_id):
        if email in self.users:
            key = str(lesson_id)
            if language not in self.users[email]['completed_lessons']:
                return False
            return key in self.users[email]['completed_lessons'][language]
        return False

    def get_studied_languages(self, email):
        if email in self.users:
            languages = []
            if self.users[email]['completed_lessons']['english']:
                languages.append("english")
            if self.users[email]['completed_lessons']['german']:
                languages.append("german")
            return languages
        return []

    def get_language_level(self, email, language):
        if email in self.users:
            return self.users[email]['language_level'].get(language, 1)
        return 1

    def get_language_xp(self, email, language):
        if email in self.users:
            return self.users[email]['language_xp'].get(language, 0)
        return 0


class AnswerButton(QPushButton):
    """Кастомная кнопка для ответов с подсветкой"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 14))
        self.setMinimumHeight(60)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 10px;
                text-align: left;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #4CAF50;
            }
        """)
        self.setCheckable(True)

    def set_highlight(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFEB3B;
                color: #333;
                border: 2px solid #FBC02D;
                border-radius: 10px;
                text-align: left;
                padding: 10px;
            }
        """)

    def set_correct(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 10px;
                text-align: left;
                padding: 10px;
            }
        """)

    def set_wrong(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: 2px solid #da190b;
                border-radius: 10px;
                text-align: left;
                padding: 10px;
            }
        """)

    def reset_style(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 10px;
                text-align: left;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #4CAF50;
            }
        """)


class MascotWidget(QLabel):
    """Виджет с маскотом-енотом Уильямом"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 75px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.sprites_dir = os.path.join(self.current_dir, "William_Raccoon")

        self.question_sprite = None
        self.right_answer_sprite = None
        self.wrong_answer_sprite = None
        self.menu_sprite = None
        self.complete_sprite = None
        self.load_sprites()

        self.set_question_mode()

    def load_sprites(self):
        try:
            question_path = os.path.join(self.sprites_dir, "William_Quastion_answer.png")
            right_path = os.path.join(self.sprites_dir, "William_Right_answer.png")
            wrong_path = os.path.join(self.sprites_dir, "William_Not_Right_answer.png")
            menu_path = os.path.join(self.sprites_dir, "William_in_Menu.png")
            complete_path = os.path.join(self.sprites_dir, "William_complete.png")

            if os.path.exists(question_path):
                self.question_sprite = QPixmap(question_path)
            if os.path.exists(right_path):
                self.right_answer_sprite = QPixmap(right_path)
            if os.path.exists(wrong_path):
                self.wrong_answer_sprite = QPixmap(wrong_path)
            if os.path.exists(menu_path):
                self.menu_sprite = QPixmap(menu_path)
            if os.path.exists(complete_path):
                self.complete_sprite = QPixmap(complete_path)
        except Exception as e:
            print(f"Ошибка загрузки спрайтов: {e}")

    def set_question_mode(self):
        if self.question_sprite:
            self.setPixmap(self.question_sprite.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("🦝❓")
            self.setFont(QFont("Segoe UI", 48))

    def set_right_answer_mode(self):
        if self.right_answer_sprite:
            self.setPixmap(self.right_answer_sprite.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("🦝🎉")
            self.setFont(QFont("Segoe UI", 48))

    def set_wrong_answer_mode(self):
        if self.wrong_answer_sprite:
            self.setPixmap(self.wrong_answer_sprite.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("🦝😔")
            self.setFont(QFont("Segoe UI", 48))

    def set_menu_mode(self):
        if self.menu_sprite:
            self.setPixmap(self.menu_sprite.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("🦝")
            self.setFont(QFont("Segoe UI", 48))

    def set_complete_mode(self):
        if self.complete_sprite:
            self.setPixmap(self.complete_sprite.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.setText("🦝🏆")
            self.setFont(QFont("Segoe UI", 48))

    def celebrate(self):
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(500)
        animation.setLoopCount(2)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        start_pos = self.pos()
        animation.setKeyValueAt(0, start_pos)
        animation.setKeyValueAt(0.5, QPoint(start_pos.x(), start_pos.y() - 20))
        animation.setKeyValueAt(1, start_pos)
        animation.start()


class FillBlankTask(QWidget):
    """Задание на заполнение пропусков в предложении"""

    def __init__(self, task_data, on_complete, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.on_complete = on_complete
        self.selected_button = None
        self.answer_buttons = []
        self.is_answered = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        sentence_parts = self.task_data['sentence'].split('___')
        sentence_label_text = sentence_parts[0] + "______" + sentence_parts[1] if len(sentence_parts) > 1 else \
        self.task_data['sentence']
        question_label = QLabel(f"📝 Заполните пропуск:\n{sentence_label_text}")
        question_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setWordWrap(True)
        layout.addWidget(question_label)

        layout.addSpacing(30)

        options_layout = QGridLayout()
        options_layout.setSpacing(10)

        options = self.task_data['options'].copy()
        random.shuffle(options)

        for i, option in enumerate(options):
            btn = AnswerButton(option)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, b=btn: self.select_answer(b))
            options_layout.addWidget(btn, i // 2, i % 2)
            self.answer_buttons.append(btn)

        layout.addLayout(options_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        self.check_btn = QPushButton("✅ Проверить")
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.clicked.connect(self.check_answer)
        button_layout.addWidget(self.check_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_answer(self, button):
        for btn in self.answer_buttons:
            btn.reset_style()
            btn.setChecked(False)
        button.setChecked(True)
        button.set_highlight()
        self.selected_button = button

    def check_answer(self):
        if self.is_answered:
            return

        if not self.selected_button:
            return

        user_answer = self.selected_button.text()
        correct_answer = self.task_data['correct']

        if user_answer == correct_answer:
            self.selected_button.set_correct()
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(True)
        else:
            self.selected_button.set_wrong()
            for btn in self.answer_buttons:
                if btn.text() == correct_answer:
                    btn.set_correct()
                    break
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(False)


class SentenceBuilderTask(QWidget):
    """Задание на составление перевода из блоков"""

    def __init__(self, sentence_data, on_complete, parent=None):
        super().__init__(parent)
        self.sentence_data = sentence_data
        self.on_complete = on_complete
        self.is_answered = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.original_label = QLabel(f"📝 Переведите на русский:\n{self.sentence_data['original']}")
        self.original_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setWordWrap(True)
        layout.addWidget(self.original_label)

        layout.addSpacing(20)

        self.drop_zone = ImprovedDropZone(self, on_word_removed=self.return_word_to_bank)
        layout.addWidget(self.drop_zone)

        layout.addSpacing(20)

        words_label = QLabel("Перетащите слова в зону выше (нажмите на слово в зоне - удалить):")
        words_label.setFont(QFont("Segoe UI", 12))
        words_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(words_label)

        all_words = self.sentence_data['words'].copy()
        random.shuffle(all_words)
        self.word_bank = WordBankWidget(all_words, on_word_removed=self.remove_word_from_bank)
        layout.addWidget(self.word_bank)

        layout.addSpacing(20)

        button_layout = QHBoxLayout()

        self.check_btn = QPushButton("✅ Проверить")
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.clicked.connect(self.check_answer)
        button_layout.addWidget(self.check_btn)

        clear_btn = QPushButton("🗑 Очистить")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_sentence)
        button_layout.addWidget(clear_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def remove_word_from_bank(self, word_text, from_dropzone=False):
        pass

    def return_word_to_bank(self, word_text, from_dropzone=True):
        self.word_bank.add_word(word_text)

    def check_answer(self):
        if self.is_answered:
            return

        user_sentence = self.drop_zone.get_sentence().strip()
        correct_sentence = self.sentence_data['translation'].strip()

        if user_sentence.lower() == correct_sentence.lower():
            self.drop_zone.highlight_correct()
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(True)
        else:
            self.drop_zone.highlight_wrong()
            self.is_answered = True
            self.check_btn.setEnabled(False)
            self.on_complete(False)

    def clear_sentence(self):
        if not self.is_answered:
            for word in self.drop_zone.words[:]:
                self.word_bank.add_word(word)
            self.drop_zone.clear_words()


class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🦝 LinguaRaccoon 🦝")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(50)

        form_frame = QFrame()
        form_frame.setMaximumWidth(400)
        form_layout = QVBoxLayout(form_frame)

        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segoe UI", 14))
        form_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите ваш email")
        self.email_input.setCursor(Qt.IBeamCursor)
        form_layout.addWidget(self.email_input)

        form_layout.addSpacing(15)

        password_label = QLabel("Пароль:")
        password_label.setFont(QFont("Segoe UI", 14))
        form_layout.addWidget(password_label)

        password_container = QWidget()
        password_container_layout = QHBoxLayout(password_container)
        password_container_layout.setContentsMargins(0, 0, 0, 0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setCursor(Qt.IBeamCursor)
        password_container_layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("👁")
        self.show_password_checkbox.setCursor(Qt.PointingHandCursor)
        self.show_password_checkbox.setToolTip("Показать/скрыть пароль")
        self.show_password_checkbox.setMaximumWidth(40)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        password_container_layout.addWidget(self.show_password_checkbox)

        form_layout.addWidget(password_container)

        form_layout.addSpacing(30)

        login_btn = QPushButton("Войти 🚀")
        login_btn.setFont(QFont("Segoe UI", 14))
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

        form_layout.addSpacing(15)

        register_btn = QPushButton("Нет аккаунта? Зарегистрироваться")
        register_btn.setStyleSheet("background-color: #2196F3;")
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(lambda: self.parent.switch_to_register())
        form_layout.addWidget(register_btn)

        layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText("Заполните все поля!")
            msg.exec_()
            return

        success, result = self.parent.db.login_user(email, password)
        if success:
            self.parent.current_user_email = email
            self.parent.current_user_data = result

            if not result.get('preferred_language'):
                self.parent.switch_to_language_selection()
            else:
                self.parent.current_language = result['preferred_language']
                self.parent.switch_to_main()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка входа")
            msg.setText(result)
            msg.exec_()


class RegisterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("📝 Регистрация")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(30)

        form_frame = QFrame()
        form_frame.setMaximumWidth(400)
        form_layout = QVBoxLayout(form_frame)

        name_label = QLabel("Имя:")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите ваше имя")
        self.name_input.setCursor(Qt.IBeamCursor)
        form_layout.addWidget(self.name_input)

        form_layout.addSpacing(15)

        email_label = QLabel("Email:")
        form_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите ваш email")
        self.email_input.setCursor(Qt.IBeamCursor)
        form_layout.addWidget(self.email_input)

        form_layout.addSpacing(15)

        password_label = QLabel("Пароль:")
        form_layout.addWidget(password_label)

        password_container = QWidget()
        password_container_layout = QHBoxLayout(password_container)
        password_container_layout.setContentsMargins(0, 0, 0, 0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setCursor(Qt.IBeamCursor)
        password_container_layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("👁")
        self.show_password_checkbox.setCursor(Qt.PointingHandCursor)
        self.show_password_checkbox.setToolTip("Показать/скрыть пароль")
        self.show_password_checkbox.setMaximumWidth(40)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        password_container_layout.addWidget(self.show_password_checkbox)

        form_layout.addWidget(password_container)

        form_layout.addSpacing(15)

        confirm_label = QLabel("Подтвердите пароль:")
        form_layout.addWidget(confirm_label)

        confirm_container = QWidget()
        confirm_container_layout = QHBoxLayout(confirm_container)
        confirm_container_layout.setContentsMargins(0, 0, 0, 0)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Повторите пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setCursor(Qt.IBeamCursor)
        confirm_container_layout.addWidget(self.confirm_input)

        self.show_confirm_checkbox = QCheckBox("👁")
        self.show_confirm_checkbox.setCursor(Qt.PointingHandCursor)
        self.show_confirm_checkbox.setToolTip("Показать/скрыть пароль")
        self.show_confirm_checkbox.setMaximumWidth(40)
        self.show_confirm_checkbox.stateChanged.connect(self.toggle_confirm_visibility)
        confirm_container_layout.addWidget(self.show_confirm_checkbox)

        form_layout.addWidget(confirm_container)

        form_layout.addSpacing(30)

        register_btn = QPushButton("Зарегистрироваться 📝")
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        form_layout.addSpacing(15)

        back_btn = QPushButton("← Назад к входу")
        back_btn.setStyleSheet("background-color: #666666;")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.parent.switch_to_login())
        form_layout.addWidget(back_btn)

        layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def toggle_password_visibility(self, state):
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def toggle_confirm_visibility(self, state):
        if state == Qt.Checked:
            self.confirm_input.setEchoMode(QLineEdit.Normal)
        else:
            self.confirm_input.setEchoMode(QLineEdit.Password)

    def register(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not name or not email or not password:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText("Заполните все поля!")
            msg.exec_()
            return

        if password != confirm:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText("Пароли не совпадают!")
            msg.exec_()
            return

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText("Введите корректный email!")
            msg.exec_()
            return

        success, result = self.parent.db.register_user(email, name, password)
        if success:
            self.parent.current_user_email = email
            self.parent.current_user_data = result
            self.parent.switch_to_language_selection()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Ошибка")
            msg.setText(result)
            msg.exec_()


class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_panel = QWidget()
        top_panel.setFixedHeight(60)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(20, 0, 20, 0)

        self.streak_label = QLabel()
        self.streak_label.setFont(QFont("Segoe UI", 14))
        top_layout.addWidget(self.streak_label)

        top_layout.addStretch()

        profile_btn = QPushButton("👤 Профиль")
        profile_btn.setMaximumWidth(150)
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.clicked.connect(lambda: self.parent.switch_to_stats())
        top_layout.addWidget(profile_btn)

        layout.addWidget(top_panel)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setSpacing(30)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def update_stats(self):
        if self.parent.current_user_data:
            self.streak_label.setText(f"🔥 Серия: {self.parent.current_user_data['streak_days']} дней")

        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lang_data = self.parent.languages[self.parent.current_language]

        title_label = QLabel(f"{lang_data['flag']} {lang_data['display_name']}")
        title_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        self.main_layout.addSpacing(20)

        # Отображение уровня языка
        lang_level = self.parent.db.get_language_level(self.parent.current_user_email, self.parent.current_language)
        lang_xp = self.parent.db.get_language_xp(self.parent.current_user_email, self.parent.current_language)

        level_frame = QFrame()
        level_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.2); border-radius: 15px; padding: 10px;")
        level_layout = QVBoxLayout(level_frame)

        level_title = QLabel(f"🏆 Уровень {lang_level} (XP: {lang_xp})")
        level_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        level_title.setAlignment(Qt.AlignCenter)
        level_layout.addWidget(level_title)

        xp_progress = QProgressBar()
        xp_progress.setMaximum(100)
        xp_progress.setValue(lang_xp % 100)
        xp_progress.setFormat(f"XP: {lang_xp % 100}/100 до следующего уровня")
        level_layout.addWidget(xp_progress)

        self.main_layout.addWidget(level_frame)
        self.main_layout.addSpacing(20)

        for theme_key, theme_data in lang_data['themes'].items():
            theme_frame = QFrame()
            theme_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(0, 0, 0, 0.2);
                    border-radius: 15px;
                    padding: 15px;
                }}
            """)
            theme_layout = QVBoxLayout(theme_frame)

            theme_title = QLabel(f"{theme_data['icon']} {theme_data['name']}")
            theme_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
            theme_title.setStyleSheet(f"color: {lang_data['color']};")
            theme_title.setAlignment(Qt.AlignCenter)
            theme_layout.addWidget(theme_title)

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("background-color: rgba(255,255,255,0.3); max-height: 2px;")
            theme_layout.addWidget(line)

            theme_layout.addSpacing(15)

            lessons_grid = QGridLayout()
            lessons_grid.setSpacing(15)

            unlocked_lessons = self.parent.current_user_data['unlocked_lessons'][self.parent.current_language]

            row = 0
            col = 0
            for lesson in theme_data['lessons']:
                lesson_id = lesson['id']
                is_unlocked = lesson_id in unlocked_lessons
                is_completed = self.parent.db.is_lesson_completed(
                    self.parent.current_user_email,
                    self.parent.current_language,
                    lesson_id
                )

                lesson_btn = QPushButton()
                lesson_btn.setCursor(Qt.PointingHandCursor)

                if is_completed:
                    lesson_btn.setText(f"✅ {lesson['title']}\n{lesson['display_title']}")
                    lesson_btn.setStyleSheet("background-color: #4CAF50;")
                    lesson_btn.clicked.connect(
                        lambda checked, lid=lesson_id, title=lesson['display_title']: self.start_completed_lesson(lid,
                                                                                                                  title))
                elif is_unlocked:
                    lesson_btn.setText(f"📚 {lesson['title']}\n{lesson['display_title']}")
                    lesson_btn.setStyleSheet("background-color: #2196F3;")
                    lesson_btn.clicked.connect(lambda checked, lid=lesson_id: self.start_lesson(lid))
                else:
                    lesson_btn.setText(f"🔒 {lesson['title']}\n{lesson['display_title']}")
                    lesson_btn.setEnabled(False)
                    lesson_btn.setStyleSheet("background-color: #666666;")

                lesson_btn.setFont(QFont("Segoe UI", 12))
                lesson_btn.setMinimumHeight(80)
                lesson_btn.setMinimumWidth(280)
                lessons_grid.addWidget(lesson_btn, row, col)
                col += 1
                if col > 2:
                    col = 0
                    row += 1

            theme_layout.addLayout(lessons_grid)
            self.main_layout.addWidget(theme_frame)
            self.main_layout.addSpacing(10)

        self.main_layout.addStretch()

        # Показываем маскота в меню
        if hasattr(self.parent, 'mascot') and self.parent.mascot:
            self.parent.mascot.set_menu_mode()
            self.parent.mascot.move(20, self.parent.height() - 170)
            self.parent.mascot.show()

    def start_completed_lesson(self, lesson_id, lesson_title):
        dialog = RepeatLessonDialog(lesson_title, self)
        if dialog.exec_() == QDialog.Accepted:
            self.start_lesson(lesson_id)

    def start_lesson(self, lesson_id):
        self.parent.switch_to_lesson(lesson_id)


class LessonPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_question_index = 0
        self.current_questions = []
        self.correct_answers = 0
        self.answer_buttons = []
        self.selected_button = None
        self.waiting_for_next = False
        self.current_lesson_id = None
        self.current_lesson_data = None
        self.mistake_questions = []
        self.is_mistake_round = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_panel = QWidget()
        top_panel.setFixedHeight(60)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(20, 0, 20, 0)

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setMaximumWidth(100)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_to_main)
        top_layout.addWidget(self.back_btn)

        top_layout.addStretch()

        self.progress_label = QLabel()
        self.progress_label.setFont(QFont("Segoe UI", 12))
        top_layout.addWidget(self.progress_label)

        layout.addWidget(top_panel)

        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.content_frame)

        self.setLayout(layout)

    def back_to_main(self):
        self.parent.switch_to_main()

    def load_lesson(self, language_key, lesson_id, lesson_data):
        self.language_key = language_key
        self.current_lesson_id = lesson_id
        self.current_lesson_data = lesson_data
        self.current_question_index = 0
        self.correct_answers = 0
        self.waiting_for_next = False
        self.mistake_questions = []
        self.is_mistake_round = False

        if self.parent.mascot:
            self.parent.mascot.set_question_mode()

        self.current_questions = self.create_unique_questions_from_lesson_data(lesson_data)
        self.show_question()

    def create_unique_questions_from_lesson_data(self, lesson_data):
        """Создание уникальных вопросов для урока (без повторений)"""
        questions = []
        used_questions = set()

        all_words = lesson_data.get('words', [])
        all_word_texts = lesson_data.get('all_words', [w[0] for w in all_words])
        all_translations = lesson_data.get('all_translations', [w[1] for w in all_words])

        for word, translation, emoji in all_words[:4]:
            q_id_1 = f"trans_to_ru_{word}"
            if q_id_1 not in used_questions:
                trans_options = self.parent.get_unique_options(translation, all_translations, 4)
                questions.append({
                    'type': 'multiple_choice',
                    'question': f"Как переводится слово {emoji} {word}?",
                    'correct': translation,
                    'options': trans_options
                })
                used_questions.add(q_id_1)

            q_id_2 = f"trans_to_en_{translation}"
            if q_id_2 not in used_questions:
                word_options = self.parent.get_unique_options(word, all_word_texts, 4)
                questions.append({
                    'type': 'multiple_choice',
                    'question': f"Как будет на {self.language_key} слово {translation}?",
                    'correct': word,
                    'options': word_options
                })
                used_questions.add(q_id_2)

        for fill_blank in lesson_data.get('fill_blanks', [])[:3]:
            q_id = f"fill_blank_{fill_blank['sentence']}"
            if q_id not in used_questions:
                questions.append({
                    'type': 'fill_blank',
                    'sentence': fill_blank['sentence'],
                    'correct': fill_blank['correct'],
                    'options': fill_blank['options']
                })
                used_questions.add(q_id)

        for translation_task in lesson_data.get('translation_tasks', [])[:3]:
            q_id = f"translation_task_{translation_task['question']}"
            if q_id not in used_questions:
                questions.append({
                    'type': 'translation_task',
                    'question': translation_task['question'],
                    'correct': translation_task['correct']
                })
                used_questions.add(q_id)

        for sentence in lesson_data.get('sentences', [])[:4]:
            q_id = f"sentence_builder_{sentence[0]}"
            if q_id not in used_questions:
                questions.append({
                    'type': 'sentence_builder',
                    'original': sentence[0],
                    'translation': sentence[1],
                    'words': sentence[2]
                })
                used_questions.add(q_id)

        random.shuffle(questions)
        return questions[:10]

    def show_question(self):
        self.clear_layout(self.content_layout)
        self.answer_buttons = []
        self.selected_button = None
        self.waiting_for_next = False

        if self.current_question_index >= len(self.current_questions):
            self.show_results()
            return

        question_data = self.current_questions[self.current_question_index]

        total_questions = len(self.current_questions)
        progress = (self.current_question_index + 1) / total_questions * 100

        if self.is_mistake_round:
            self.progress_label.setText(
                f"Исправление ошибок: {self.current_question_index + 1} из {len(self.current_questions)}")
        else:
            self.progress_label.setText(f"Вопрос {self.current_question_index + 1} из {total_questions}")

        progress_bar = QProgressBar()
        progress_bar.setValue(int(progress))
        progress_bar.setMaximumHeight(20)
        self.content_layout.addWidget(progress_bar)

        self.content_layout.addSpacing(30)

        if question_data['type'] == 'sentence_builder':
            self.sentence_task = SentenceBuilderTask(
                question_data,
                self.on_task_complete
            )
            self.content_layout.addWidget(self.sentence_task)
        elif question_data['type'] == 'fill_blank':
            self.fill_task = FillBlankTask(
                question_data,
                self.on_task_complete
            )
            self.content_layout.addWidget(self.fill_task)
        elif question_data['type'] == 'translation_task':
            self.translation_task = TranslationTask(
                question_data,
                self.on_task_complete
            )
            self.content_layout.addWidget(self.translation_task)
        else:
            question_label = QLabel(question_data['question'])
            question_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
            question_label.setAlignment(Qt.AlignCenter)
            question_label.setWordWrap(True)
            self.content_layout.addWidget(question_label)

            self.content_layout.addSpacing(30)

            options_layout = QGridLayout()
            options_layout.setSpacing(10)

            options = question_data['options'].copy()
            random.shuffle(options)

            for i, option in enumerate(options):
                btn = AnswerButton(option)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, b=btn: self.select_answer(b))
                options_layout.addWidget(btn, i // 2, i % 2)
                self.answer_buttons.append(btn)

            self.content_layout.addLayout(options_layout)
            self.content_layout.addSpacing(20)

            button_layout = QHBoxLayout()
            check_btn = QPushButton("✅ Проверить")
            check_btn.setCursor(Qt.PointingHandCursor)
            check_btn.clicked.connect(self.check_answer)
            button_layout.addWidget(check_btn)

            self.content_layout.addLayout(button_layout)

    def select_answer(self, button):
        if self.waiting_for_next:
            return
        for btn in self.answer_buttons:
            btn.reset_style()
            btn.setChecked(False)
        button.setChecked(True)
        button.set_highlight()
        self.selected_button = button

    def on_task_complete(self, is_correct):
        if is_correct:
            self.correct_answers += 1
            if self.parent.mascot:
                self.parent.mascot.set_right_answer_mode()
            self.schedule_next_question()
        else:
            if not self.is_mistake_round:
                question_data = self.current_questions[self.current_question_index]
                self.mistake_questions.append(question_data)
            if self.parent.mascot:
                self.parent.mascot.set_wrong_answer_mode()
            self.schedule_next_question()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def check_answer(self):
        if self.waiting_for_next or not self.selected_button:
            return

        question_data = self.current_questions[self.current_question_index]
        user_answer = self.selected_button.text()
        correct_answer = question_data['correct']

        if user_answer == correct_answer:
            self.correct_answers += 1
            self.selected_button.set_correct()
            if self.parent.mascot:
                self.parent.mascot.set_right_answer_mode()
            self.waiting_for_next = True
            for btn in self.answer_buttons:
                btn.setEnabled(False)
            self.schedule_next_question()
        else:
            self.selected_button.set_wrong()
            for btn in self.answer_buttons:
                if btn.text() == correct_answer:
                    btn.set_correct()
                    break

            if not self.is_mistake_round:
                self.mistake_questions.append(question_data)

            if self.parent.mascot:
                self.parent.mascot.set_wrong_answer_mode()
            self.waiting_for_next = True
            for btn in self.answer_buttons:
                btn.setEnabled(False)
            self.schedule_next_question()

    def schedule_next_question(self):
        QTimer.singleShot(2000, self.next_question)

    def next_question(self):
        self.waiting_for_next = False
        self.current_question_index += 1

        if not self.is_mistake_round and self.current_question_index >= len(
                self.current_questions) and self.mistake_questions:
            self.is_mistake_round = True
            self.current_questions = self.mistake_questions.copy()
            self.mistake_questions = []
            self.current_question_index = 0
            self.correct_answers = 0
            self.show_question()
            return

        self.show_question()

    def show_results(self):
        self.clear_layout(self.content_layout)

        success, xp_reward = self.parent.db.complete_lesson(
            self.parent.current_user_email,
            self.language_key,
            self.current_lesson_id
        )

        self.parent.db.unlock_next_lesson(
            self.parent.current_user_email,
            self.language_key,
            self.current_lesson_id
        )

        if self.parent.mascot:
            self.parent.mascot.celebrate()
            self.parent.mascot.set_complete_mode()

        self.parent.current_user_data = self.parent.db.users[self.parent.current_user_email]

        repeat_count = self.parent.db.get_lesson_repeat_count(self.parent.current_user_email, self.language_key,
                                                              self.current_lesson_id)
        is_repeat = repeat_count > 1

        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        results_layout.setAlignment(Qt.AlignCenter)

        if is_repeat:
            result_label = QLabel(f"🔄 Повторение урока: {self.current_lesson_data['display_title']}")
        else:
            result_label = QLabel(f"📊 Результаты урока: {self.current_lesson_data['display_title']}")
        result_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        result_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(result_label)

        results_layout.addSpacing(20)

        if self.parent.mascot:
            mascot_container = QWidget()
            mascot_layout = QHBoxLayout(mascot_container)
            mascot_layout.setAlignment(Qt.AlignCenter)
            mascot_layout.addWidget(self.parent.mascot)
            results_layout.addWidget(mascot_container)
            results_layout.addSpacing(20)

        score_label = QLabel(f"Правильных ответов: {self.correct_answers} из 10")
        score_label.setFont(QFont("Segoe UI", 18))
        score_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(score_label)

        lang_xp = self.parent.db.get_language_xp(self.parent.current_user_email, self.language_key)
        lang_level = self.parent.db.get_language_level(self.parent.current_user_email, self.language_key)

        if is_repeat:
            xp_label = QLabel(f"✨ Получено XP за повторение: {xp_reward} ✨")
        else:
            xp_label = QLabel(f"✨ Получено XP: {xp_reward} ✨")
        xp_label.setFont(QFont("Segoe UI", 16))
        xp_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(xp_label)

        total_xp_label = QLabel(f"📊 Общий XP языка {self.language_key.capitalize()}: {lang_xp} | Уровень: {lang_level}")
        total_xp_label.setFont(QFont("Segoe UI", 14))
        total_xp_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(total_xp_label)

        results_layout.addSpacing(30)

        if is_repeat:
            message = f"🎉 Урок пройден повторно! Вы получили {xp_reward} XP! 🎉"
        else:
            message = f"🎉 Урок пройден! Вы получили {xp_reward} XP! 🎉"
        next_unlocked = self.current_lesson_id + 1 in self.parent.current_user_data['unlocked_lessons'][
            self.language_key]
        if next_unlocked:
            message += " Следующий урок разблокирован!"

        message_label = QLabel(message)
        message_label.setFont(QFont("Segoe UI", 16))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        results_layout.addWidget(message_label)

        results_layout.addSpacing(40)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        menu_btn = QPushButton("🏠 Главное меню")
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.clicked.connect(self.back_to_main)
        button_layout.addWidget(menu_btn)

        results_layout.addLayout(button_layout)

        self.content_layout.addWidget(results_container, alignment=Qt.AlignCenter)


class StatsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        top_panel = QWidget()
        top_panel.setFixedHeight(60)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(20, 0, 20, 0)

        back_btn = QPushButton("← Назад")
        back_btn.setMaximumWidth(100)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.parent.switch_to_main())
        top_layout.addWidget(back_btn)

        logout_btn = QPushButton("🚪 Выход")
        logout_btn.setMaximumWidth(100)
        logout_btn.setStyleSheet("background-color: #f44336;")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(logout_btn)

        layout.addWidget(top_panel)

        title = QLabel("👤 Профиль пользователя")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(30)

        self.stats_frame = QFrame()
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.stats_frame)

        change_lang_btn = QPushButton("🌍 Сменить язык изучения")
        change_lang_btn.setMaximumWidth(250)
        change_lang_btn.setCursor(Qt.PointingHandCursor)
        change_lang_btn.clicked.connect(lambda: self.parent.switch_to_language_selection())
        layout.addWidget(change_lang_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def logout(self):
        dialog = ExitConfirmationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.parent.logout()

    def update_stats(self):
        while self.stats_layout.count():
            widget = self.stats_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        if not self.parent.current_user_data:
            return

        user = self.parent.current_user_data

        studied_languages = self.parent.db.get_studied_languages(self.parent.current_user_email)
        studied_languages_display = []
        lang_stats = {}

        for lang in studied_languages:
            if lang == "english":
                lang_name = "🇬🇧 Английский"
                studied_languages_display.append(lang_name)
                lang_stats[
                    lang_name] = f"Уровень {self.parent.db.get_language_level(self.parent.current_user_email, 'english')} (XP: {self.parent.db.get_language_xp(self.parent.current_user_email, 'english')})"
            elif lang == "german":
                lang_name = "🇩🇪 Немецкий"
                studied_languages_display.append(lang_name)
                lang_stats[
                    lang_name] = f"Уровень {self.parent.db.get_language_level(self.parent.current_user_email, 'german')} (XP: {self.parent.db.get_language_xp(self.parent.current_user_email, 'german')})"

        studied_languages_str = ", ".join(
            studied_languages_display) if studied_languages_display else "Нет пройденных уроков"

        stats = {
            "👤 Имя пользователя": user['name'],
            "📧 Email": self.parent.current_user_email,
            "🔥 Текущая серия": f"{user['streak_days']} дней",
            "🌍 Изучаемые языки": studied_languages_str,
            "📅 Дата регистрации": datetime.fromisoformat(user['join_date']).strftime("%d.%m.%Y")
        }

        for key, value in stats.items():
            stat_widget = QWidget()
            stat_layout = QHBoxLayout(stat_widget)

            key_label = QLabel(f"{key}:")
            key_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            key_label.setStyleSheet("color: white;")
            stat_layout.addWidget(key_label)

            stat_layout.addStretch()

            value_label = QLabel(str(value))
            value_label.setFont(QFont("Segoe UI", 16))
            value_label.setStyleSheet("color: white;")
            stat_layout.addWidget(value_label)

            self.stats_layout.addWidget(stat_widget)
            self.stats_layout.addSpacing(10)

        if lang_stats:
            self.stats_layout.addSpacing(20)
            for lang_name, lang_value in lang_stats.items():
                stat_widget = QWidget()
                stat_layout = QHBoxLayout(stat_widget)

                key_label = QLabel(f"{lang_name}:")
                key_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
                key_label.setStyleSheet("color: white;")
                stat_layout.addWidget(key_label)

                stat_layout.addStretch()

                value_label = QLabel(lang_value)
                value_label.setFont(QFont("Segoe UI", 16))
                value_label.setStyleSheet("color: white;")
                stat_layout.addWidget(value_label)

                self.stats_layout.addWidget(stat_widget)
                self.stats_layout.addSpacing(10)


class LinguaRaccoonApp(QMainWindow):
    """Главное приложение для изучения языков LinguaRaccoon"""

    def __init__(self):
        super().__init__()
        self.db = UserDatabase()
        self.current_user_email = None
        self.current_user_data = None
        self.current_language = "english"
        self.current_lesson = None
        self.mascot = None
        self.init_ui()
        self.load_data()
        self.check_auto_login()
        self.showMaximized()

    def check_auto_login(self):
        if self.db.current_session and self.db.current_session in self.db.users:
            self.current_user_email = self.db.current_session
            self.current_user_data = self.db.users[self.db.current_session]
            if self.current_user_data.get('preferred_language'):
                self.current_language = self.current_user_data['preferred_language']
            self.switch_to_main()

    def init_ui(self):
        self.setWindowTitle("LinguaRaccoon")
        self.setMinimumSize(1200, 700)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_page = LoginPage(self)
        self.register_page = RegisterPage(self)
        self.main_page = MainPage(self)
        self.lesson_page = LessonPage(self)
        self.stats_page = StatsPage(self)
        self.language_selection_page = LanguageSelectionPage(self)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.lesson_page)
        self.stacked_widget.addWidget(self.stats_page)
        self.stacked_widget.addWidget(self.language_selection_page)

        self.apply_styles()

        # Создаём маскота для отображения в меню
        self.mascot = MascotWidget(self)
        self.mascot.move(20, self.height() - 170)
        self.mascot.set_menu_mode()
        # Показываем маскота только на главной странице
        self.mascot.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.mascot and self.stacked_widget.currentWidget() == self.main_page:
            self.mascot.move(20, self.height() - 170)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                color: white;
            }
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                color: black;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def load_data(self):
        self.languages = {
            "english": {
                "name": "🇬🇧 English",
                "display_name": "Английский",
                "flag": "🇬🇧",
                "color": "#FF6B6B",
                "themes": {
                    "greetings": {
                        "name": "👋 Приветствие",
                        "icon": "👋",
                        "lessons": [
                            {"id": 1, "title": "Basic Greetings", "display_title": "Основные приветствия"},
                            {"id": 2, "title": "Polite Phrases", "display_title": "Вежливые фразы"},
                            {"id": 3, "title": "Farewells", "display_title": "Прощания"}
                        ]
                    },
                    "family": {
                        "name": "👨‍👩‍👧‍👦 Семья",
                        "icon": "👨‍👩‍👧‍👦",
                        "lessons": [
                            {"id": 4, "title": "Family Members", "display_title": "Члены семьи"},
                            {"id": 5, "title": "Describing Family", "display_title": "Описание семьи"},
                            {"id": 6, "title": "Family Activities", "display_title": "Семейные занятия"}
                        ]
                    },
                    "basic_phrases": {
                        "name": "💬 Основные фразы",
                        "icon": "💬",
                        "lessons": [
                            {"id": 7, "title": "Common Questions", "display_title": "Частые вопросы"},
                            {"id": 8, "title": "Daily Expressions", "display_title": "Ежедневные выражения"},
                            {"id": 9, "title": "Emergency Phrases", "display_title": "Экстренные фразы"},
                            {"id": 10, "title": "Small Talk", "display_title": "Разговорные фразы"}
                        ]
                    },
                    "animals": {
                        "name": "🐾 Животные",
                        "icon": "🐾",
                        "lessons": [
                            {"id": 11, "title": "Pets", "display_title": "Домашние питомцы"},
                            {"id": 12, "title": "Wild Animals", "display_title": "Дикие животные"},
                            {"id": 13, "title": "Farm Animals", "display_title": "Сельскохозяйственные животные"}
                        ]
                    },
                    "numbers": {
                        "name": "🔢 Цифры",
                        "icon": "🔢",
                        "lessons": [
                            {"id": 14, "title": "Numbers 0-10", "display_title": "Числа 0-10"},
                            {"id": 15, "title": "Numbers 10-50", "display_title": "Числа 10-50"},
                            {"id": 16, "title": "Numbers 50-100", "display_title": "Числа 50-100"}
                        ]
                    },
                    "colors": {
                        "name": "🎨 Цвета",
                        "icon": "🎨",
                        "lessons": [
                            {"id": 17, "title": "Basic Colors", "display_title": "Основные цвета"},
                            {"id": 18, "title": "Shades", "display_title": "Оттенки"},
                            {"id": 19, "title": "Color Expressions", "display_title": "Цветовые выражения"},
                            {"id": 20, "title": "Describing with Colors", "display_title": "Описание цветами"}
                        ]
                    },
                    "time": {
                        "name": "⏰ Время",
                        "icon": "⏰",
                        "lessons": [
                            {"id": 21, "title": "Days of Week", "display_title": "Дни недели"},
                            {"id": 22, "title": "Months", "display_title": "Месяцы"},
                            {"id": 23, "title": "Seasons", "display_title": "Времена года"},
                            {"id": 24, "title": "Telling Time", "display_title": "Который час"},
                            {"id": 25, "title": "Time Expressions", "display_title": "Временные выражения"}
                        ]
                    }
                }
            },
            "german": {
                "name": "🇩🇪 Deutsch",
                "display_name": "Немецкий",
                "flag": "🇩🇪",
                "color": "#4ECDC4",
                "themes": {
                    "greetings": {
                        "name": "👋 Begrüßung",
                        "icon": "👋",
                        "lessons": [
                            {"id": 1, "title": "Grundlegende Begrüßungen", "display_title": "Основные приветствия"},
                            {"id": 2, "title": "Höfliche Ausdrücke", "display_title": "Вежливые выражения"},
                            {"id": 3, "title": "Verabschiedungen", "display_title": "Прощания"}
                        ]
                    },
                    "family": {
                        "name": "👨‍👩‍👧‍👦 Familie",
                        "icon": "👨‍👩‍👧‍👦",
                        "lessons": [
                            {"id": 4, "title": "Familienmitglieder", "display_title": "Члены семьи"},
                            {"id": 5, "title": "Familie beschreiben", "display_title": "Описание семьи"},
                            {"id": 6, "title": "Familienaktivitäten", "display_title": "Семейные занятия"}
                        ]
                    },
                    "basic_phrases": {
                        "name": "💬 Grundlegende Sätze",
                        "icon": "💬",
                        "lessons": [
                            {"id": 7, "title": "Häufige Fragen", "display_title": "Частые вопросы"},
                            {"id": 8, "title": "Tägliche Ausdrücke", "display_title": "Ежедневные выражения"},
                            {"id": 9, "title": "Notfallausdrücke", "display_title": "Экстренные выражения"},
                            {"id": 10, "title": "Small Talk", "display_title": "Разговорные фразы"}
                        ]
                    },
                    "animals": {
                        "name": "🐾 Tiere",
                        "icon": "🐾",
                        "lessons": [
                            {"id": 11, "title": "Haustiere", "display_title": "Домашние питомцы"},
                            {"id": 12, "title": "Wilde Tiere", "display_title": "Дикие животные"},
                            {"id": 13, "title": "Nutztiere", "display_title": "Сельскохозяйственные животные"}
                        ]
                    },
                    "numbers": {
                        "name": "🔢 Zahlen",
                        "icon": "🔢",
                        "lessons": [
                            {"id": 14, "title": "Zahlen 0-10", "display_title": "Числа 0-10"},
                            {"id": 15, "title": "Zahlen 10-50", "display_title": "Числа 10-50"},
                            {"id": 16, "title": "Zahlen 50-100", "display_title": "Числа 50-100"}
                        ]
                    },
                    "colors": {
                        "name": "🎨 Farben",
                        "icon": "🎨",
                        "lessons": [
                            {"id": 17, "title": "Grundfarben", "display_title": "Основные цвета"},
                            {"id": 18, "title": "Farbtöne", "display_title": "Оттенки"},
                            {"id": 19, "title": "Farbausdrücke", "display_title": "Цветовые выражения"},
                            {"id": 20, "title": "Mit Farben beschreiben", "display_title": "Описание цветами"}
                        ]
                    },
                    "time": {
                        "name": "⏰ Zeit",
                        "icon": "⏰",
                        "lessons": [
                            {"id": 21, "title": "Wochentage", "display_title": "Дни недели"},
                            {"id": 22, "title": "Monate", "display_title": "Месяцы"},
                            {"id": 23, "title": "Jahreszeiten", "display_title": "Времена года"},
                            {"id": 24, "title": "Uhrzeit", "display_title": "Который час"},
                            {"id": 25, "title": "Zeitausdrücke", "display_title": "Временные выражения"}
                        ]
                    }
                }
            }
        }

        self.lesson_data = {}
        self.init_lesson_data()

    def init_lesson_data(self):
        self.lesson_data["english"] = {
            1: self.get_english_lesson_1(),
            2: self.get_english_lesson_2(),
            3: self.get_english_lesson_3(),
        }

        self.lesson_data["german"] = {
            1: self.get_german_lesson_1(),
            2: self.get_german_lesson_2(),
            3: self.get_german_lesson_3(),
        }

        for i in range(4, 26):
            self.lesson_data["english"][i] = self.get_english_lesson_1()
            self.lesson_data["german"][i] = self.get_german_lesson_1()

    def get_unique_options(self, correct, all_options, count=4):
        options = [correct]
        available = [opt for opt in all_options if opt != correct and opt not in options]
        available = list(dict.fromkeys(available))
        random.shuffle(available)

        for opt in available:
            if len(options) < count:
                options.append(opt)

        if len(options) < count:
            fallbacks = ["Welcome", "Goodbye", "Sorry", "Please", "Thanks", "Morning", "Evening", "Night"]
            for fb in fallbacks:
                if fb not in options and len(options) < count:
                    options.append(fb)

        random.shuffle(options)
        return options[:count]

    def get_english_lesson_1(self):
        all_words = ["Hello", "Good morning", "Good afternoon", "Good evening"]
        all_translations = ["Привет", "Доброе утро", "Добрый день", "Добрый вечер"]

        return {
            "title": "Basic Greetings",
            "display_title": "Основные приветствия",
            "words": [("Hello", "Привет", "👋"), ("Good morning", "Доброе утро", "🌅"),
                      ("Good afternoon", "Добрый день", "☀️"), ("Good evening", "Добрый вечер", "🌆")],
            "sentences": [
                ("Hello, how are you?", "привет как дела",
                 ["Привет", "как", "дела", "здравствуйте", "пока", "спасибо", "доброе", "утро"]),
                ("Good morning, my friend", "доброе утро мой друг",
                 ["Доброе", "утро", "мой", "друг", "привет", "пока", "хорошо", "день"])
            ],
            "fill_blanks": [
                {"sentence": "___ are you?", "correct": "How", "options": ["How", "What", "Where", "Who"]},
                {"sentence": "Good ___, my friend", "correct": "morning",
                 "options": ["morning", "afternoon", "evening", "night"]}
            ],
            "translation_tasks": [
                {"question": "Hello", "correct": "привет"},
                {"question": "Good morning", "correct": "доброе утро"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_english_lesson_2(self):
        all_words = ["Please", "Thank you", "Sorry", "Excuse me"]
        all_translations = ["Пожалуйста", "Спасибо", "Извините", "Простите"]

        return {
            "title": "Polite Phrases",
            "display_title": "Вежливые фразы",
            "words": [("Please", "Пожалуйста", "🙏"), ("Thank you", "Спасибо", "🙏"),
                      ("Sorry", "Извините", "😔"), ("Excuse me", "Простите", "🙏")],
            "sentences": [
                ("Thank you very much", "большое спасибо",
                 ["Большое", "спасибо", "пожалуйста", "извините", "простите", "помогите", "доброе"]),
                ("Please help me", "пожалуйста помогите мне",
                 ["Пожалуйста", "помогите", "мне", "спасибо", "извините", "простите", "его", "её"])
            ],
            "fill_blanks": [
                {"sentence": "Thank ___ very much", "correct": "you", "options": ["you", "me", "him", "her"]},
                {"sentence": "___ me, where is the station?", "correct": "Excuse",
                 "options": ["Excuse", "Sorry", "Please", "Thank"]}
            ],
            "translation_tasks": [
                {"question": "Thank you", "correct": "спасибо"},
                {"question": "Please", "correct": "пожалуйста"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_english_lesson_3(self):
        all_words = ["Goodbye", "Bye", "See you", "Good night"]
        all_translations = ["До свидания", "Пока", "Увидимся", "Спокойной ночи"]

        return {
            "title": "Farewells",
            "display_title": "Прощания",
            "words": [("Goodbye", "До свидания", "👋"), ("Bye", "Пока", "👋"),
                      ("See you", "Увидимся", "👋"), ("Good night", "Спокойной ночи", "🌙")],
            "sentences": [
                ("Goodbye, see you tomorrow", "до свидания увидимся завтра",
                 ["До", "свидания", "увидимся", "завтра", "пока", "привет", "хорошо", "день"]),
                ("Have a nice day", "хорошего дня",
                 ["Хорошего", "дня", "пока", "спасибо", "доброе", "утро", "привет", "до"])
            ],
            "fill_blanks": [
                {"sentence": "Good ___, see you later", "correct": "bye",
                 "options": ["bye", "night", "morning", "day"]},
                {"sentence": "See you ___", "correct": "tomorrow", "options": ["tomorrow", "today", "soon", "later"]}
            ],
            "translation_tasks": [
                {"question": "Goodbye", "correct": "до свидания"},
                {"question": "Good night", "correct": "спокойной ночи"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_german_lesson_1(self):
        all_words = ["Hallo", "Guten Morgen", "Guten Tag", "Guten Abend"]
        all_translations = ["Привет", "Доброе утро", "Добрый день", "Добрый вечер"]

        return {
            "title": "Grundlegende Begrüßungen",
            "display_title": "Основные приветствия",
            "words": [("Hallo", "Привет", "👋"), ("Guten Morgen", "Доброе утро", "🌅"),
                      ("Guten Tag", "Добрый день", "☀️"), ("Guten Abend", "Добрый вечер", "🌆")],
            "sentences": [
                ("Hallo, wie geht es dir?", "привет как дела",
                 ["Привет", "как", "дела", "здравствуйте", "пока", "спасибо", "доброе", "утро"]),
                ("Guten Morgen, mein Freund", "доброе утро мой друг",
                 ["Доброе", "утро", "мой", "друг", "привет", "пока", "хорошо", "день"])
            ],
            "fill_blanks": [
                {"sentence": "___ geht es dir?", "correct": "Wie", "options": ["Wie", "Was", "Wo", "Wann"]},
                {"sentence": "Guten ___, mein Freund", "correct": "Morgen",
                 "options": ["Morgen", "Tag", "Abend", "Nacht"]}
            ],
            "translation_tasks": [
                {"question": "Hallo", "correct": "привет"},
                {"question": "Guten Morgen", "correct": "доброе утро"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_german_lesson_2(self):
        all_words = ["Bitte", "Danke", "Entschuldigung", "Gern geschehen"]
        all_translations = ["Пожалуйста", "Спасибо", "Извините", "Пожалуйста"]

        return {
            "title": "Höfliche Ausdrücke",
            "display_title": "Вежливые выражения",
            "words": [("Bitte", "Пожалуйста", "🙏"), ("Danke", "Спасибо", "🙏"),
                      ("Entschuldigung", "Извините", "😔"), ("Gern geschehen", "Пожалуйста", "🙏")],
            "sentences": [
                ("Danke schön", "большое спасибо",
                 ["Большое", "спасибо", "пожалуйста", "извините", "простите", "помогите", "доброе"]),
                ("Bitte helfen Sie mir", "пожалуйста помогите мне",
                 ["Пожалуйста", "помогите", "мне", "спасибо", "извините", "простите", "его", "её"])
            ],
            "fill_blanks": [
                {"sentence": "Danke ___!", "correct": "schön", "options": ["schön", "sehr", "gut", "bitte"]},
                {"sentence": "___ Sie mir bitte", "correct": "Helfen",
                 "options": ["Helfen", "Sagen", "Geben", "Zeigen"]}
            ],
            "translation_tasks": [
                {"question": "Danke", "correct": "спасибо"},
                {"question": "Bitte", "correct": "пожалуйста"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_german_lesson_3(self):
        all_words = ["Auf Wiedersehen", "Tschüss", "Bis bald", "Gute Nacht"]
        all_translations = ["До свидания", "Пока", "До скорого", "Спокойной ночи"]

        return {
            "title": "Verabschiedungen",
            "display_title": "Прощания",
            "words": [("Auf Wiedersehen", "До свидания", "👋"), ("Tschüss", "Пока", "👋"),
                      ("Bis bald", "До скорого", "👋"), ("Gute Nacht", "Спокойной ночи", "🌙")],
            "sentences": [
                ("Auf Wiedersehen, bis morgen", "до свидания до завтра",
                 ["До", "свидания", "до", "завтра", "пока", "привет", "хорошо", "день"]),
                ("Gute Nacht und schlaf gut", "спокойной ночи и спи хорошо",
                 ["Спокойной", "ночи", "и", "спи", "хорошо", "пока", "доброе", "утро"])
            ],
            "fill_blanks": [
                {"sentence": "Auf ___, bis morgen", "correct": "Wiedersehen",
                 "options": ["Wiedersehen", "passen", "pass", "Wieder"]},
                {"sentence": "Gute ___", "correct": "Nacht", "options": ["Nacht", "Tag", "Morgen", "Abend"]}
            ],
            "translation_tasks": [
                {"question": "Auf Wiedersehen", "correct": "до свидания"},
                {"question": "Gute Nacht", "correct": "спокойной ночи"}
            ],
            "all_words": all_words,
            "all_translations": all_translations
        }

    def get_lesson_data(self, language, lesson_id):
        if language in self.lesson_data and lesson_id in self.lesson_data[language]:
            return self.lesson_data[language][lesson_id]
        return None

    def switch_language(self, language):
        self.current_language = language
        if self.current_user_data:
            self.db.set_preferred_language(self.current_user_email, language)
        self.main_page.update_stats()

    def switch_to_login(self):
        self.stacked_widget.setCurrentWidget(self.login_page)
        if self.mascot:
            self.mascot.hide()

    def switch_to_register(self):
        self.stacked_widget.setCurrentWidget(self.register_page)
        if self.mascot:
            self.mascot.hide()

    def switch_to_main(self):
        self.main_page.update_stats()
        self.stacked_widget.setCurrentWidget(self.main_page)
        if self.mascot:
            self.mascot.set_menu_mode()
            self.mascot.move(20, self.height() - 170)
            self.mascot.show()

    def switch_to_lesson(self, lesson_id):
        self.current_lesson = lesson_id
        lesson_data = self.get_lesson_data(self.current_language, lesson_id)
        if lesson_data:
            if self.mascot:
                self.mascot.set_question_mode()
            self.lesson_page.load_lesson(self.current_language, lesson_id, lesson_data)
            self.stacked_widget.setCurrentWidget(self.lesson_page)
        else:
            QMessageBox.warning(self, "Ошибка", f"Данные для урока {lesson_id} не найдены!")

    def switch_to_stats(self):
        self.stats_page.update_stats()
        self.stacked_widget.setCurrentWidget(self.stats_page)
        if self.mascot:
            self.mascot.set_menu_mode()
            self.mascot.move(20, self.height() - 170)
            self.mascot.show()

    def switch_to_language_selection(self):
        self.stacked_widget.setCurrentWidget(self.language_selection_page)
        if self.mascot:
            self.mascot.set_menu_mode()
            self.mascot.move(20, self.height() - 170)
            self.mascot.show()

    def logout(self):
        dialog = ExitConfirmationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.db.logout()
            self.current_user_email = None
            self.current_user_data = None
            self.switch_to_login()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LinguaRaccoon")
    app.setStyle('Fusion')

    window = LinguaRaccoonApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()