"""Тестовая часть для приложения LinguaRaccoon Тестирование всех компонентов и функций"""

import unittest
import json
import os
import sys
import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Импорты PyQt5 для GUI тестов
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QMimeData, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen, QBrush
from PyQt5.QtTest import QTest

#Импортируем все необходимые классы из основного приложения
from lingua_raccoon import (
    LinguaRaccoonApp,
    UserDatabase,
    DraggableWord,
    ImprovedDropZone,
    WordBankWidget,
    AnswerButton,
    TranslationTask,
    FillBlankTask,
    SentenceBuilderTask,
    RepeatLessonDialog,
    ExitConfirmationDialog,
    LoginPage,
    RegisterPage,
    MainPage,
    LessonPage,
    StatsPage,
    LanguageSelectionPage,
    MascotWidget,
)


class TestUserDatabase(unittest.TestCase):
    """Тестирую все функции класса UserDatabase"""

    def setUp(self):
        """Готовлю временные файлы для каждого теста"""
        self.test_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.test_dir, "users_data.json")
        self.session_file = os.path.join(self.test_dir, "current_session.json")

        self.db = UserDatabase()
        self.db.users_file = self.users_file
        self.db.current_session_file = self.session_file

        self.db.users = {}
        self.db.current_session = None
        self.db.save_users()

    def tearDown(self):
        """Удаляю временные файлы после теста"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_register_user_success(self):
        """Проверяю успешную регистрацию пользователя"""
        success, user_data = self.db.register_user(
            "test@example.com",
            "Test User",
            "password123"
        )

        self.assertTrue(success)
        self.assertEqual(user_data['name'], "Test User")
        self.assertIn("test@example.com", self.db.users)

        user = self.db.users["test@example.com"]
        self.assertEqual(user['name'], "Test User")
        self.assertEqual(user['password'], "password123")
        self.assertIn('join_date', user)
        self.assertIn('last_login', user)
        self.assertEqual(user['preferred_language'], 'english')
        self.assertEqual(user['unlocked_lessons']['english'], [1])
        self.assertEqual(user['language_xp']['english'], 0)
        self.assertEqual(user['language_level']['english'], 1)
        self.assertEqual(user['streak_days'], 0)

    def test_02_register_user_duplicate(self):
        """Проверяю, что нельзя зарегистрироваться с существующим email"""
        self.db.register_user("test@example.com", "Test User", "password123")

        success, message = self.db.register_user(
            "test@example.com",
            "Another User",
            "password456"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Пользователь с таким email уже существует")

    def test_03_login_user_success(self):
        """Проверяю успешный вход пользователя"""
        self.db.register_user("test@example.com", "Test User", "password123")

        success, user_data = self.db.login_user("test@example.com", "password123")

        self.assertTrue(success)
        self.assertEqual(user_data['name'], "Test User")
        self.assertEqual(self.db.current_session, "test@example.com")

    def test_04_login_user_wrong_password(self):
        """Проверяю вход с неверным паролем"""
        self.db.register_user("test@example.com", "Test User", "password123")

        success, message = self.db.login_user("test@example.com", "wrongpassword")

        self.assertFalse(success)
        self.assertEqual(message, "Неверный пароль")

    def test_05_login_user_not_found(self):
        """Проверяю вход несуществующего пользователя"""
        success, message = self.db.login_user("nonexistent@example.com", "password")

        self.assertFalse(success)
        self.assertEqual(message, "Пользователь не найден")

    def test_06_save_and_load_users(self):
        """Проверяю сохранение и загрузку пользователей"""
        self.db.register_user("test@example.com", "Test User", "password123")
        self.db.save_users()

        self.assertTrue(os.path.exists(self.users_file))

        new_db = UserDatabase()
        new_db.users_file = self.users_file
        new_db.current_session_file = self.session_file
        new_db.load_users()

        self.assertIn("test@example.com", new_db.users)
        self.assertEqual(new_db.users["test@example.com"]['name'], "Test User")

    def test_07_save_and_load_session(self):
        """Проверяю сохранение и загрузку сессии"""
        self.db.save_current_session("test@example.com")

        self.assertTrue(os.path.exists(self.session_file))

        new_db = UserDatabase()
        new_db.current_session_file = self.session_file
        new_db.load_current_session()

        self.assertEqual(new_db.current_session, "test@example.com")

    def test_08_set_preferred_language(self):
        """Проверяю установку предпочитаемого языка"""
        self.db.register_user("test@example.com", "Test User", "password123")

        self.db.set_preferred_language("test@example.com", "german")

        user = self.db.users["test@example.com"]
        self.assertEqual(user['preferred_language'], "german")

        self.db.set_preferred_language("test@example.com", "english")
        self.assertEqual(user['preferred_language'], "english")

    def test_09_add_language_xp(self):
        """Проверяю добавление опыта и повышение уровня"""
        self.db.register_user("test@example.com", "Test User", "password123")

        self.db.add_language_xp("test@example.com", "english", 50)
        user = self.db.users["test@example.com"]
        self.assertEqual(user['language_xp']['english'], 50)
        self.assertEqual(user['language_level']['english'], 1)

        self.db.add_language_xp("test@example.com", "english", 60)
        self.assertEqual(user['language_xp']['english'], 110)
        self.assertEqual(user['language_level']['english'], 2)

    def test_10_complete_lesson_first_time(self):
        """Проверяю первое прохождение урока"""
        self.db.register_user("test@example.com", "Test User", "password123")

        success, xp = self.db.complete_lesson("test@example.com", "english", 1)

        self.assertTrue(success)
        self.assertEqual(xp, 50)
        self.assertTrue(
            self.db.is_lesson_completed("test@example.com", "english", 1)
        )

        user = self.db.users["test@example.com"]
        self.assertEqual(user['language_xp']['english'], 50)

    def test_11_complete_lesson_repeat(self):
        """Проверяю повторное прохождение урока"""
        self.db.register_user("test@example.com", "Test User", "password123")

        self.db.complete_lesson("test@example.com", "english", 1)
        user = self.db.users["test@example.com"]
        self.assertEqual(user['language_xp']['english'], 50)

        success, xp = self.db.complete_lesson("test@example.com", "english", 1)

        self.assertTrue(success)
        self.assertEqual(xp, 20)
        self.assertEqual(user['language_xp']['english'], 70)

        repeat_count = self.db.get_lesson_repeat_count(
            "test@example.com", "english", 1
        )
        self.assertEqual(repeat_count, 2)

    def test_12_unlock_next_lesson(self):
        """Проверяю разблокировку следующего урока"""
        self.db.register_user("test@example.com", "Test User", "password123")

        user = self.db.users["test@example.com"]
        self.assertIn(1, user['unlocked_lessons']['english'])
        self.assertNotIn(2, user['unlocked_lessons']['english'])

        self.db.unlock_next_lesson("test@example.com", "english", 1)
        self.assertIn(2, user['unlocked_lessons']['english'])

    def test_13_update_streak(self):
        """Проверяю обновление серии дней"""
        self.db.register_user("test@example.com", "Test User", "password123")
        user = self.db.users["test@example.com"]

        self.db.update_streak("test@example.com")
        self.assertEqual(user['streak_days'], 1)
        self.assertIsNotNone(user['last_streak_date'])

    def test_14_get_studied_languages(self):
        """Проверяю получение списка изучаемых языков"""
        self.db.register_user("test@example.com", "Test User", "password123")

        languages = self.db.get_studied_languages("test@example.com")
        self.assertEqual(languages, [])

        self.db.complete_lesson("test@example.com", "english", 1)
        languages = self.db.get_studied_languages("test@example.com")
        self.assertIn("english", languages)

        self.db.complete_lesson("test@example.com", "german", 1)
        languages = self.db.get_studied_languages("test@example.com")
        self.assertIn("german", languages)
        self.assertEqual(len(languages), 2)

    def test_15_get_language_level(self):
        """Проверяю получение уровня языка"""
        self.db.register_user("test@example.com", "Test User", "password123")

        level = self.db.get_language_level("test@example.com", "english")
        self.assertEqual(level, 1)

        self.db.add_language_xp("test@example.com", "english", 150)
        level = self.db.get_language_level("test@example.com", "english")
        self.assertEqual(level, 2)

    def test_16_get_language_xp(self):
        """Проверяю получение опыта в языке"""
        self.db.register_user("test@example.com", "Test User", "password123")

        xp = self.db.get_language_xp("test@example.com", "english")
        self.assertEqual(xp, 0)

        self.db.add_language_xp("test@example.com", "english", 75)
        xp = self.db.get_language_xp("test@example.com", "english")
        self.assertEqual(xp, 75)

    def test_17_get_lesson_repeat_count(self):
        """Проверяю получение количества повторений урока"""
        self.db.register_user("test@example.com", "Test User", "password123")

        count = self.db.get_lesson_repeat_count("test@example.com", "english", 1)
        self.assertEqual(count, 0)

        self.db.complete_lesson("test@example.com", "english", 1)
        count = self.db.get_lesson_repeat_count("test@example.com", "english", 1)
        self.assertEqual(count, 1)

        self.db.complete_lesson("test@example.com", "english", 1)
        count = self.db.get_lesson_repeat_count("test@example.com", "english", 1)
        self.assertEqual(count, 2)

    def test_18_is_lesson_completed(self):
        """Проверяю статус завершения урока"""
        self.db.register_user("test@example.com", "Test User", "password123")

        self.assertFalse(
            self.db.is_lesson_completed("test@example.com", "english", 1)
        )

        self.db.complete_lesson("test@example.com", "english", 1)

        self.assertTrue(
            self.db.is_lesson_completed("test@example.com", "english", 1)
        )

        self.assertFalse(
            self.db.is_lesson_completed("test@example.com", "english", 2)
        )

    def test_19_clear_current_session(self):
        """Проверяю очистку сессии при выходе"""
        self.db.register_user("test@example.com", "Test User", "password123")
        self.db.save_current_session("test@example.com")

        self.assertEqual(self.db.current_session, "test@example.com")

        self.db.clear_current_session()
        self.assertIsNone(self.db.current_session)
        self.assertFalse(os.path.exists(self.session_file))

    def test_20_reset_user_data(self):
        """Проверяю инициализацию данных пользователя"""
        incomplete_data = {
            'name': 'Test User',
            'password': 'password123'
        }

        reset_data = self.db.reset_user_data(incomplete_data)

        self.assertIn('join_date', reset_data)
        self.assertIn('last_login', reset_data)
        self.assertIn('preferred_language', reset_data)
        self.assertIn('unlocked_lessons', reset_data)
        self.assertIn('completed_lessons', reset_data)
        self.assertIn('language_xp', reset_data)
        self.assertIn('language_level', reset_data)
        self.assertIn('streak_days', reset_data)

        self.assertEqual(reset_data['preferred_language'], 'english')
        self.assertEqual(reset_data['unlocked_lessons']['english'], [1])
        self.assertEqual(reset_data['language_xp']['english'], 0)
        self.assertEqual(reset_data['streak_days'], 0)
        self.assertIsNone(reset_data['last_streak_date'])


class TestDraggableWord(unittest.TestCase):
    """Тестирую перетаскиваемые слова"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

    def test_01_create_draggable_word(self):
        """Проверяю создание перетаскиваемого слова"""
        word = DraggableWord("Hello")
        self.assertEqual(word.text(), "Hello")
        self.assertFalse(word.is_in_dropzone)
        self.assertEqual(word.cursor().shape(), Qt.PointingHandCursor)
        self.assertEqual(word.minimumWidth(), 100)
        self.assertEqual(word.minimumHeight(), 50)

    def test_02_create_word_in_dropzone(self):
        """Проверяю создание слова в зоне сброса"""
        word = DraggableWord("Hello", is_in_dropzone=True)
        self.assertTrue(word.is_in_dropzone)
        self.assertIn("background-color: #2196F3", word.styleSheet())

    def test_03_update_style(self):
        """Проверяю обновление стиля слова"""
        word = DraggableWord("Hello", is_in_dropzone=False)
        self.assertIn("background-color: #4CAF50", word.styleSheet())

        word.is_in_dropzone = True
        word.update_style()
        self.assertIn("background-color: #2196F3", word.styleSheet())

    def test_04_set_correct_style(self):
        """Проверяю стиль правильного ответа"""
        word = DraggableWord("Hello")
        word.set_correct_style()
        self.assertIn("background-color: #4CAF50", word.styleSheet())
        self.assertIn("border: 2px solid #2E7D32", word.styleSheet())

    def test_05_set_wrong_style(self):
        """Проверяю стиль неправильного ответа"""
        word = DraggableWord("Hello")
        word.set_wrong_style()
        self.assertIn("background-color: #f44336", word.styleSheet())
        self.assertIn("border: 2px solid #c62828", word.styleSheet())

    def test_06_mouse_press_event(self):
        """Проверяю обработку нажатия мыши для перетаскивания"""
        word = DraggableWord("Hello")

        event = Mock()
        event.button.return_value = Qt.LeftButton

        word.mousePressEvent(event)

        self.assertIsNotNone(word.mimeData)

    def test_07_mouse_double_click_event(self):
        """Проверяю двойной клик для возврата слова из зоны"""
        return_called = False

        def on_return(word):
            nonlocal return_called
            return_called = True
            self.assertEqual(word.text(), "Hello")

        word = DraggableWord("Hello", is_in_dropzone=True, on_return=on_return)

        event = Mock()
        word.mouseDoubleClickEvent(event)

        self.assertTrue(return_called)

    def test_08_mouse_double_click_outside_dropzone(self):
        """Проверяю двойной клик для слов вне зоны сброса"""
        return_called = False

        def on_return(word):
            nonlocal return_called
            return_called = True

        word = DraggableWord("Hello", is_in_dropzone=False, on_return=on_return)

        event = Mock()
        word.mouseDoubleClickEvent(event)

        self.assertFalse(return_called)


class TestImprovedDropZone(unittest.TestCase):
    """Тестирую зону для сборки предложений"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.drop_zone = ImprovedDropZone()
        self.removed_words = []
        self.drop_zone.on_word_removed = self.on_word_removed

    def on_word_removed(self, word_text, from_dropzone):
        self.removed_words.append((word_text, from_dropzone))

    def test_01_create_drop_zone(self):
        """Проверяю создание зоны сброса"""
        self.assertIsNotNone(self.drop_zone.layout)
        self.assertEqual(len(self.drop_zone.words), 0)
        self.assertEqual(len(self.drop_zone.word_widgets), 0)
        self.assertTrue(self.drop_zone.acceptDrops())

    def test_02_add_word(self):
        """Проверяю добавление слова в зону"""
        self.drop_zone.add_word("Hello")

        self.assertEqual(len(self.drop_zone.words), 1)
        self.assertEqual(self.drop_zone.words[0], "Hello")
        self.assertEqual(len(self.drop_zone.word_widgets), 1)

        widget = self.drop_zone.word_widgets[0]
        self.assertTrue(widget.is_in_dropzone)
        self.assertEqual(widget.text(), "Hello")

    def test_03_add_multiple_words(self):
        """Проверяю добавление нескольких слов"""
        words = ["Hello", "World", "Test"]
        for word in words:
            self.drop_zone.add_word(word)

        self.assertEqual(len(self.drop_zone.words), 3)
        self.assertEqual(self.drop_zone.words, words)

    def test_04_get_sentence(self):
        """Проверяю получение предложения из зоны"""
        words = ["Hello", "World"]
        for word in words:
            self.drop_zone.add_word(word)

        sentence = self.drop_zone.get_sentence()
        self.assertEqual(sentence, "Hello World")

    def test_05_clear_words(self):
        """Проверяю очистку всех слов из зоны"""
        self.drop_zone.add_word("Hello")
        self.drop_zone.add_word("World")

        self.assertEqual(len(self.drop_zone.words), 2)

        self.drop_zone.clear_words()

        self.assertEqual(len(self.drop_zone.words), 0)
        self.assertEqual(len(self.drop_zone.word_widgets), 0)

    def test_06_highlight_correct(self):
        """Проверяю подсветку правильного ответа"""
        self.drop_zone.add_word("Hello")
        self.drop_zone.add_word("World")

        self.drop_zone.highlight_correct()

        for widget in self.drop_zone.word_widgets:
            self.assertIn("background-color: #4CAF50", widget.styleSheet())

    def test_07_highlight_wrong(self):
        """Проверяю подсветку неправильного ответа"""
        self.drop_zone.add_word("Hello")
        self.drop_zone.add_word("World")

        self.drop_zone.highlight_wrong()

        for widget in self.drop_zone.word_widgets:
            self.assertIn("background-color: #f44336", widget.styleSheet())

    def test_08_return_word(self):
        """Проверяю возврат слова в банк"""
        self.drop_zone.add_word("Hello")
        word_widget = self.drop_zone.word_widgets[0]

        self.assertEqual(len(self.drop_zone.words), 1)
        self.assertEqual(len(self.drop_zone.word_widgets), 1)

        self.drop_zone.return_word(word_widget)

        self.assertEqual(len(self.drop_zone.words), 0)
        self.assertEqual(len(self.drop_zone.word_widgets), 0)
        self.assertEqual(len(self.removed_words), 1)
        self.assertEqual(self.removed_words[0][0], "Hello")
        self.assertTrue(self.removed_words[0][1])


class TestWordBankWidget(unittest.TestCase):
    """Тестирую банк слов"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.words = ["Hello", "World", "Test"]
        self.removed_words = []
        self.word_bank = WordBankWidget(
            self.words.copy(),
            on_word_removed=self.on_word_removed
        )

    def on_word_removed(self, word_text, from_dropzone):
        self.removed_words.append((word_text, from_dropzone))

    def test_01_create_word_bank(self):
        """Проверяю создание банка слов"""
        self.assertEqual(len(self.word_bank.words), 3)
        self.assertEqual(len(self.word_bank.word_widgets), 3)
        self.assertEqual(self.word_bank.words, ["Hello", "World", "Test"])

    def test_02_add_word(self):
        """Проверяю добавление слова в банк"""
        self.word_bank.add_word("NewWord")

        self.assertIn("NewWord", self.word_bank.words)
        self.assertEqual(len(self.word_bank.word_widgets), 4)

        widget = self.word_bank.word_widgets[-1]
        self.assertFalse(widget.is_in_dropzone)
        self.assertEqual(widget.text(), "NewWord")

    def test_03_update_words(self):
        """Проверяю обновление списка слов"""
        new_words = ["A", "B", "C"]
        self.word_bank.words = new_words
        self.word_bank.update_words()

        self.assertEqual(len(self.word_bank.word_widgets), 3)
        for i, word in enumerate(new_words):
            self.assertEqual(self.word_bank.word_widgets[i].text(), word)

    def test_04_remove_word(self):
        """Проверяю удаление слова из банка"""
        widget = self.word_bank.word_widgets[0]
        word_text = self.word_bank.words[0]

        self.word_bank.remove_word(widget)

        self.assertNotIn(word_text, self.word_bank.words)
        self.assertEqual(len(self.word_bank.word_widgets), 2)
        self.assertEqual(len(self.removed_words), 1)
        self.assertEqual(self.removed_words[0][0], word_text)
        self.assertFalse(self.removed_words[0][1])


class TestAnswerButton(unittest.TestCase):
    """Тестирую кнопки ответов"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

    def test_01_create_answer_button(self):
        """Проверяю создание кнопки ответа"""
        btn = AnswerButton("Test")
        self.assertEqual(btn.text(), "Test")
        self.assertTrue(btn.isCheckable())
        self.assertEqual(btn.minimumHeight(), 60)
        self.assertEqual(btn.cursor().shape(), Qt.PointingHandCursor)

    def test_02_set_highlight(self):
        """Проверяю подсветку выбранной кнопки"""
        btn = AnswerButton("Test")
        btn.set_highlight()
        self.assertIn("background-color: #FFEB3B", btn.styleSheet())

    def test_03_set_correct(self):
        """Проверяю стиль правильного ответа"""
        btn = AnswerButton("Test")
        btn.set_correct()
        self.assertIn("background-color: #4CAF50", btn.styleSheet())

    def test_04_set_wrong(self):
        """Проверяю стиль неправильного ответа"""
        btn = AnswerButton("Test")
        btn.set_wrong()
        self.assertIn("background-color: #f44336", btn.styleSheet())

    def test_05_reset_style(self):
        """Проверяю сброс стиля кнопки"""
        btn = AnswerButton("Test")
        btn.set_highlight()
        btn.reset_style()
        self.assertIn("background-color: white", btn.styleSheet())


class TestMascotWidget(unittest.TestCase):
    """Тестирую маскота-енота"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.mascot = MascotWidget()

    def test_01_create_mascot(self):
        """Проверяю создание маскота"""
        self.assertEqual(self.mascot.width(), 150)
        self.assertEqual(self.mascot.height(), 150)
        self.assertEqual(self.mascot.alignment(), Qt.AlignCenter)
        self.assertTrue(self.mascot.scaledContents())

    def test_02_load_sprites(self):
        """Проверяю загрузку спрайтов"""
        self.mascot.load_sprites()

        self.assertIsNotNone(self.mascot.question_sprite)
        self.assertIsNotNone(self.mascot.right_answer_sprite)
        self.assertIsNotNone(self.mascot.wrong_answer_sprite)
        self.assertIsNotNone(self.mascot.menu_sprite)
        self.assertIsNotNone(self.mascot.complete_sprite)

    def test_03_set_question_mode(self):
        """Проверяю режим вопроса"""
        self.mascot.set_question_mode()
        self.assertTrue(
            self.mascot.pixmap() is not None or self.mascot.text() is not None
        )

    def test_04_set_right_answer_mode(self):
        """Проверяю режим правильного ответа"""
        self.mascot.set_right_answer_mode()
        self.assertTrue(
            self.mascot.pixmap() is not None or self.mascot.text() is not None
        )

    def test_05_set_wrong_answer_mode(self):
        """Проверяю режим неправильного ответа"""
        self.mascot.set_wrong_answer_mode()
        self.assertTrue(
            self.mascot.pixmap() is not None or self.mascot.text() is not None
        )

    def test_06_set_menu_mode(self):
        """Проверяю режим меню"""
        self.mascot.set_menu_mode()
        self.assertTrue(
            self.mascot.pixmap() is not None or self.mascot.text() is not None
        )

    def test_07_set_complete_mode(self):
        """Проверяю режим завершения"""
        self.mascot.set_complete_mode()
        self.assertTrue(
            self.mascot.pixmap() is not None or self.mascot.text() is not None
        )

    def test_08_celebrate(self):
        """Проверяю анимацию празднования"""
        start_pos = self.mascot.pos()

        self.mascot.celebrate()

        self.assertIsNotNone(self.mascot.animation)
        self.assertEqual(self.mascot.animation.duration(), 500)
        self.assertEqual(self.mascot.animation.loopCount(), 2)


class TestDialogs(unittest.TestCase):
    """Тестирую диалоговые окна"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

    def test_01_repeat_lesson_dialog(self):
        """Проверяю диалог повторения урока"""
        dialog = RepeatLessonDialog("Test Lesson")

        self.assertEqual(dialog.windowTitle(), "Повторение урока")
        self.assertTrue(dialog.isModal())
        self.assertEqual(dialog.width(), 400)
        self.assertEqual(dialog.height(), 200)

        self.assertIsNotNone(dialog.yes_btn)
        self.assertIsNotNone(dialog.no_btn)

    def test_02_exit_confirmation_dialog(self):
        """Проверяю диалог подтверждения выхода"""
        dialog = ExitConfirmationDialog()

        self.assertEqual(dialog.windowTitle(), "Подтверждение выхода")
        self.assertTrue(dialog.isModal())
        self.assertEqual(dialog.width(), 400)
        self.assertEqual(dialog.height(), 200)

        self.assertIsNotNone(dialog.yes_btn)
        self.assertIsNotNone(dialog.no_btn)


class TestLessonPageComponents(unittest.TestCase):
    """Тестирую компоненты страницы уроков"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.completed = []

        def on_complete(is_correct):
            self.completed.append(is_correct)

        self.on_complete = on_complete

    def test_01_translation_task_creation(self):
        """Проверяю создание задания на перевод"""
        task_data = {
            "question": "Hello",
            "correct": "привет"
        }
        task = TranslationTask(task_data, self.on_complete)

        self.assertEqual(task.task_data['question'], "Hello")
        self.assertEqual(task.task_data['correct'], "привет")
        self.assertFalse(task.is_answered)
        self.assertIsNotNone(task.answer_input)

    def test_02_translation_task_check_correct(self):
        """Проверяю правильный перевод"""
        task_data = {
            "question": "Hello",
            "correct": "привет"
        }
        task = TranslationTask(task_data, self.on_complete)

        task.answer_input.setText("привет")
        task.check_answer()

        self.assertTrue(task.is_answered)
        self.assertFalse(task.check_btn.isEnabled())
        self.assertEqual(len(self.completed), 1)
        self.assertTrue(self.completed[0])

    def test_03_translation_task_check_wrong(self):
        """Проверяю неправильный перевод"""
        task_data = {
            "question": "Hello",
            "correct": "привет"
        }
        task = TranslationTask(task_data, self.on_complete)

        task.answer_input.setText("пока")
        task.check_answer()

        self.assertTrue(task.is_answered)
        self.assertFalse(task.check_btn.isEnabled())
        self.assertEqual(len(self.completed), 1)
        self.assertFalse(self.completed[0])

    def test_04_fill_blank_task_creation(self):
        """Проверяю создание задания на заполнение пропуска"""
        task_data = {
            "sentence": "___ world",
            "correct": "Hello",
            "options": ["Hello", "Hi", "Hey", "Good"]
        }
        task = FillBlankTask(task_data, self.on_complete)

        self.assertEqual(task.task_data['sentence'], "___ world")
        self.assertEqual(task.task_data['correct'], "Hello")
        self.assertFalse(task.is_answered)
        self.assertEqual(len(task.answer_buttons), 4)

    def test_05_fill_blank_task_select_answer(self):
        """Проверяю выбор ответа в задании с пропуском"""
        task_data = {
            "sentence": "___ world",
            "correct": "Hello",
            "options": ["Hello", "Hi", "Hey", "Good"]
        }
        task = FillBlankTask(task_data, self.on_complete)

        button = task.answer_buttons[0]
        task.select_answer(button)

        self.assertEqual(task.selected_button, button)
        self.assertTrue(button.isChecked())

    def test_06_fill_blank_task_check_correct(self):
        """Проверяю правильное заполнение пропуска"""
        task_data = {
            "sentence": "___ world",
            "correct": "Hello",
            "options": ["Hello", "Hi", "Hey", "Good"]
        }
        task = FillBlankTask(task_data, self.on_complete)

        correct_button = task.answer_buttons[0]
        task.select_answer(correct_button)
        task.check_answer()

        self.assertTrue(task.is_answered)
        self.assertFalse(task.check_btn.isEnabled())
        self.assertEqual(len(self.completed), 1)
        self.assertTrue(self.completed[0])
        self.assertIn("background-color: #4CAF50", correct_button.styleSheet())

    def test_07_fill_blank_task_check_wrong(self):
        """Проверяю неправильное заполнение пропуска"""
        task_data = {
            "sentence": "___ world",
            "correct": "Hello",
            "options": ["Hello", "Hi", "Hey", "Good"]
        }
        task = FillBlankTask(task_data, self.on_complete)

        wrong_button = task.answer_buttons[1]
        task.select_answer(wrong_button)
        task.check_answer()

        self.assertTrue(task.is_answered)
        self.assertFalse(task.check_btn.isEnabled())
        self.assertEqual(len(self.completed), 1)
        self.assertFalse(self.completed[0])
        self.assertIn("background-color: #f44336", wrong_button.styleSheet())


class TestLinguaRaccoonApp(unittest.TestCase):
    """Тестирую главное приложение"""

    def setUp(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.test_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.test_dir, "users_data.json")
        self.session_file = os.path.join(self.test_dir, "current_session.json")

        self.window = LinguaRaccoonApp()
        self.window.db.users_file = self.users_file
        self.window.db.current_session_file = self.session_file
        self.window.db.users = {}
        self.window.db.current_session = None
        self.window.db.save_users()

    def tearDown(self):
        if hasattr(self, 'window'):
            self.window.close()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_create_application(self):
        """Проверяю создание главного окна приложения"""
        self.assertEqual(self.window.windowTitle(), "LinguaRaccoon")
        self.assertIsNotNone(self.window.stacked_widget)
        self.assertIsNotNone(self.window.db)
        self.assertIsNotNone(self.window.login_page)
        self.assertIsNotNone(self.window.register_page)
        self.assertIsNotNone(self.window.main_page)
        self.assertIsNotNone(self.window.lesson_page)
        self.assertIsNotNone(self.window.stats_page)
        self.assertIsNotNone(self.window.language_selection_page)

    def test_02_switch_to_login(self):
        """Проверяю переключение на страницу входа"""
        self.window.switch_to_login()
        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.login_page
        )
        self.assertTrue(self.window.mascot.isHidden())

    def test_03_switch_to_register(self):
        """Проверяю переключение на страницу регистрации"""
        self.window.switch_to_register()
        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.register_page
        )
        self.assertTrue(self.window.mascot.isHidden())

    def test_04_switch_to_main(self):
        """Проверяю переключение на главную страницу"""
        self.window.db.register_user("test@example.com", "Test User", "password123")
        self.window.current_user_email = "test@example.com"
        self.window.current_user_data = self.window.db.users["test@example.com"]

        self.window.switch_to_main()
        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.main_page
        )
        self.assertFalse(self.window.mascot.isHidden())

    def test_05_switch_to_stats(self):
        """Проверяю переключение на страницу статистики"""
        self.window.db.register_user("test@example.com", "Test User", "password123")
        self.window.current_user_email = "test@example.com"
        self.window.current_user_data = self.window.db.users["test@example.com"]

        self.window.switch_to_stats()
        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.stats_page
        )
        self.assertFalse(self.window.mascot.isHidden())

    def test_06_switch_to_language_selection(self):
        """Проверяю переключение на страницу выбора языка"""
        self.window.switch_to_language_selection()
        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.language_selection_page
        )
        self.assertFalse(self.window.mascot.isHidden())

    def test_07_get_lesson_data_english(self):
        """Проверяю получение данных английского урока"""
        lesson = self.window.get_lesson_data("english", 1)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson['title'], "Basic Greetings")
        self.assertEqual(lesson['display_title'], "Основные приветствия")
        self.assertTrue(len(lesson['words']) > 0)
        self.assertTrue(len(lesson['sentences']) > 0)

        lesson = self.window.get_lesson_data("english", 2)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson['title'], "Polite Phrases")

    def test_08_get_lesson_data_german(self):
        """Проверяю получение данных немецкого урока"""
        lesson = self.window.get_lesson_data("german", 1)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson['title'], "Grundlegende Begrüßungen")
        self.assertEqual(lesson['display_title'], "Основные приветствия")
        self.assertTrue(len(lesson['words']) > 0)

        lesson = self.window.get_lesson_data("german", 2)
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson['title'], "Höfliche Ausdrücke")

    def test_09_get_lesson_data_nonexistent(self):
        """Проверяю обработку несуществующего урока"""
        lesson = self.window.get_lesson_data("english", 999)
        self.assertIsNone(lesson)

    def test_10_get_unique_options(self):
        """Проверяю создание уникальных вариантов ответов"""
        all_options = ["Hello", "Hi", "Hey", "Good", "Morning", "Evening"]
        options = self.window.get_unique_options("Hello", all_options, 4)

        self.assertEqual(len(options), 4)
        self.assertIn("Hello", options)
        self.assertTrue(len(set(options)) == 4)

    def test_11_get_unique_options_with_fallback(self):
        """Проверяю использование запасных вариантов"""
        all_options = ["Hello", "Hi"]
        options = self.window.get_unique_options("Hello", all_options, 4)

        self.assertEqual(len(options), 4)
        self.assertIn("Hello", options)
        self.assertIn("Welcome", options)
        self.assertIn("Goodbye", options)

    def test_12_switch_to_lesson(self):
        """Проверяю загрузку урока"""
        self.window.db.register_user("test@example.com", "Test User", "password123")
        self.window.current_user_email = "test@example.com"
        self.window.current_user_data = self.window.db.users["test@example.com"]
        self.window.current_language = "english"

        self.window.switch_to_lesson(1)

        self.assertEqual(
            self.window.stacked_widget.currentWidget(),
            self.window.lesson_page
        )
        self.assertEqual(self.window.current_lesson, 1)
        self.assertIsNotNone(self.window.lesson_page.current_lesson_data)

    def test_13_switch_to_lesson_not_found(self):
        """Проверяю обработку несуществующего урока"""
        self.window.current_language = "english"

        with self.assertRaises(Exception):
            self.window.switch_to_lesson(999)

    def test_14_apply_styles(self):
        """Проверяю применение стилей"""
        style = self.window.styleSheet()
        self.assertIn("background", style)
        self.assertIn("QPushButton", style)
        self.assertIn("QLabel", style)

    def test_15_resize_event(self):
        """Проверяю обработку изменения размера окна"""
        initial_pos = self.window.mascot.pos()

        self.window.resize(800, 600)

        if self.window.stacked_widget.currentWidget() == self.window.main_page:
            self.assertNotEqual(self.window.mascot.pos(), initial_pos)

    def test_16_check_auto_login(self):
        """Проверяю автоматический вход"""
        self.window.db.register_user("test@example.com", "Test User", "password123")
        self.window.db.save_current_session("test@example.com")

        new_window = LinguaRaccoonApp()
        new_window.db.users_file = self.users_file
        new_window.db.current_session_file = self.session_file
        new_window.db.load_users()
        new_window.db.load_current_session()
        new_window.check_auto_login()

        self.assertEqual(new_window.current_user_email, "test@example.com")
        self.assertIsNotNone(new_window.current_user_data)

        new_window.close()


def run_tests():
    """Запускаю все тесты"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestUserDatabase,
        TestDraggableWord,
        TestImprovedDropZone,
        TestWordBankWidget,
        TestAnswerButton,
        TestMascotWidget,
        TestDialogs,
        TestLessonPageComponents,
        TestLinguaRaccoonApp,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\nСВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Неудач: {len(result.failures)}")

    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✅")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ! ❌")

        if result.errors:
            print("\nОшибки (Errors):")
            for test, traceback in result.errors:
                print(f"  - {test}")
                print(f"    {traceback[:200]}...")

        if result.failures:
            print("\nНеудачи (Failures):")
            for test, traceback in result.failures:
                print(f"  - {test}")
                print(f"    {traceback[:200]}...")

    return result.wasSuccessful()


def main():
    """Главная функция для запуска тестов"""
    print("\nЗАПУСК ТЕСТИРОВАНИЯ ПРИЛОЖЕНИЯ LINGUARACCOON")
    print("Тестирование включает:")
    print("  - База данных пользователей (20 тестов)")
    print("  - Перетаскиваемые слова (8 тестов)")
    print("  - Зона сборки предложений (8 тестов)")
    print("  - Банк слов (4 теста)")
    print("  - Кнопки ответов (5 тестов)")
    print("  - Маскот-енот (8 тестов)")
    print("  - Диалоговые окна (2 теста)")
    print("  - Компоненты уроков (7 тестов)")
    print("  - Главное приложение (16 тестов)\n")

    success = run_tests()

    print("\n" + ("✅" if success else "❌") + " СТАТУС: " + ("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if success else "ТЕСТЫ НЕ ПРОЙДЕНЫ"))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
