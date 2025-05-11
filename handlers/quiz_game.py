import os
import sqlite3
from aiogram.types import FSInputFile, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot, F, Router
from keyboards import kb_replay
from .hendlers_state import GPTStateRequests
from html import escape
import openai
import difflib
import httpx

quiz_router = Router()

#Константы
IMAGE_PATH = "resources/images/quiz.jpg"
PROMPT_FILE = "resources/prompts/quiz.txt"
DB_NAME = "quiz_results.db"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    BASE_PROMPT = f.read().strip()

TOPICS = {
    "quiz_prog": ("Программирование python", "quiz_prog"),
    "quiz_math": ("Математика, алгебра, геометрия", "quiz_math"),
    "quiz_biology": ("Биология", "quiz_biology")
}


class QuizGame:
    def __init__(self, bot: Bot):
        '''Инициализирует SQLite базу данных.
        Инициализирует GPT клиент с прокси.'''
        self.bot = bot
        self.init_db()
        self._gpt_token = os.getenv('GPT_TOKEN')
        self._proxy = os.getenv('PROXY_GPT')
        self._client = self._create_client()

    def _create_client(self):
        '''Создаёт асинхронный клиент OpenAI с поддержкой прокси через httpx'''
        gpt_client = openai.AsyncOpenAI(
            api_key=self._gpt_token,
            http_client=httpx.AsyncClient(
                proxy=self._proxy
            )
        )
        return gpt_client

    @staticmethod
    def init_db():
        """Создаёт таблицу results, если её ещё нет."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    user_answer TEXT,
                    correct_answer TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    async def start_quiz(message: Message, user_id: int):
        """Показывает пользователю кнопки тем квиза в виде инлайн-клавиатуры."""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💻 Программирование", callback_data="quiz_prog")],
            [InlineKeyboardButton(text="🧮 Математика", callback_data="quiz_math")],
            [InlineKeyboardButton(text="🔬 Биология", callback_data="quiz_biology")],
        ])

        await message.answer("Выберите тему квиза:", reply_markup=keyboard)

    async def handle_quiz_choice(self, callback_query: CallbackQuery, state: FSMContext, topic_key: str):
        '''Получает тему из callback_data.
        Запрашивает GPT новый вопрос и ответ.
        Отправляет фото и текст вопроса'''
        await callback_query.answer()

        if topic_key == "quiz_more":
            data = await state.get_data()
            if not data or "topic" not in data:
                await callback_query.message.answer("Сначала выберите тему!")
                return
            topic_key = data["topic"]

        topic_desc = topic_key

        try:
            question, correct_answer = await self.generate_quiz(topic_desc)

            await state.update_data(
                topic=topic_key,
                question=question,
                correct_answer=correct_answer
            )

            await state.set_state(GPTStateRequests.quiz_game)

            photo = FSInputFile(IMAGE_PATH)
            await self.bot.send_photo(
                chat_id=callback_query.from_user.id,
                photo=photo,
                caption=f"❓ Вопрос: {question}"
            )
        except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при генерации вопроса: {escape(str(e))}")

    async def generate_quiz(self, topic_desc):
        '''Составляет промпт на основе темы.
        Вызывает GPT-3.5-Turbo.
        Парсит ответ'''
        prompt = BASE_PROMPT + '\nФормат вывода:\nВопрос: ...\nОтвет: ...\nОТВЕЧАЙ СТРОГО В ЭТОМ ФОРМАТЕ!' + f"\nСоставь вопрос по теме: {topic_desc}"

        print(f"[DEBUG] Промт:\n{prompt}")

        try:
            response = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content.strip()
            print(f"[DEBUG] Ответ от GPT:\n{content}")

            if not content:
                raise ValueError("Пустой ответ от GPT")

            if 'Вопрос:' not in content or 'Ответ:' not in content:
                print(f'prompt = {prompt}')
                print(f'content = {content}')
                await self.generate_quiz(topic_desc)

            lines = [line for line in content.split('\n') if line.strip()]
            question_line = next(line for line in lines if line.startswith("Вопрос:"))
            answer_line = next(line for line in lines if line.startswith("Ответ:"))

            question = question_line.replace("Вопрос:", "").strip()
            answer = answer_line.replace("Ответ:", "").strip()

            return question, answer

        except StopIteration as e:
            raise Exception("Не удалось найти строку с вопросом или ответом. Убедитесь, что GPT следует формату.")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            await self.generate_quiz(self, topic_desc)
            raise Exception(f"Ошибка при генерации вопроса: {e}")

    async def evaluate_answer(self, message: Message, state: FSMContext):
        """Сравнивает ответ пользователя с правильным.
            Формирует обратную связь.
            Предлагает действия: «Еще вопрос», «Статистика» и т.д.
            Сохраняет результат в БД."""
        print(f"[DEBUG] Текущий user_id: {message.from_user.id}")
        data = await state.get_data()
        correct_answer = data["correct_answer"].lower()
        user_answer = message.text.strip().lower()
        question = data["question"]
        topic = data["topic"]

        score = await self.evaluate_answer_with_gpt(correct_answer, user_answer, topic)

        if score == 10:
            feedback = f"✅ Правильно!\nОценка: {score}/10"
        else:
            feedback = f"❌ Неправильно! Правильный ответ: {correct_answer.capitalize()}\nОценка: {score}/10"
            if score >= 6:
                feedback += "\nХорошо, но можно точнее!"
            elif score >= 3:
                feedback += "\nБлизко, но не совсем."
            elif score == 0:
                feedback += "\nМимо."
            else:
                feedback += "\nПочти мимо."

        await message.answer(feedback, parse_mode=None)

        self.save_result_to_db(message.from_user.id, topic, question, user_answer, correct_answer, score)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔁 Еще вопрос", callback_data="quiz_again"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="quiz_stats")
            ]
        ])
        await message.answer("Выберите действие:", reply_markup=keyboard)

        await state.update_data(question=None, correct_answer=None)

    async def evaluate_answer_with_gpt(self, correct_answer: str, user_answer: str, topic_desc: str) -> int:
        '''Отправляет GPT информацию о правильном и пользовательском ответе.
            Получает числовую оценку (0–10).
            Возвращает число как оценку.'''

        prompt = f"""
    Твоя задача — оценить, насколько пользовательский ответ соответствует правильному по смыслу.
    Оцени ответ по шкале от 0 до 10:
    - 10 — полностью верно
    - 5 — частично верно или общий смысл есть
    - 0 — совсем неверно или не относится к теме
    Не пиши объяснений, только одно число.

    Тема: {topic_desc}
    Правильный ответ: {correct_answer}
    Ответ пользователя: {user_answer}
    """

        try:
            response = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=10
            )

            content = response.choices[0].message.content.strip()

            if content.isdigit():
                score = int(content)
            else:
                # Логируем неправильный ответ GPT
                print(f"[WARNING] GPT вернул нечисловой ответ: '{content}'")
                score = 0

            return max(0, min(10, score))

        except Exception as e:
            print(f"[ERROR] Ошибка при оценке через GPT: {e}")
            return 0

    def save_result_to_db(self, user_id, topic, question, user_answer, correct_answer, score):
        '''Записывает:
            ID пользователя.
            Тему.
            Вопрос и ответы.
            Оценку.'''

        print(f"[DEBUG] Сохраняем результат:")
        print(f"user_id: {user_id}")
        print(f"topic: {topic}")
        print(f"question: {question}")
        print(f"user_answer: {user_answer}")
        print(f"correct_answer: {correct_answer}")
        print(f"score: {score}")

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO results (user_id, topic, question, user_answer, correct_answer, score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, topic, question, user_answer, correct_answer, score))
                conn.commit()
                print(f"[SUCCESS] Запись успешно добавлена в БД")
        except Exception as e:
            print(f"[ERROR] Не удалось сохранить в БД: {e}")

    def calculate_similarity(self, a, b):
        """Возвращает коэффициент схожести двух строк."""
        return difflib.SequenceMatcher(None, a, b).ratio()

    async def show_stats(self, user_id, message: Message):
        """Показывает статистику пользователя по темам.
        Делает выборку из БД.
        Вычисляет средний балл.
        Выводит статистику по темам."""

        print(f"[DEBUG] Текущий user_id: {user_id}")

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM results WHERE user_id=?", (user_id,))
            all_rows = cursor.fetchall()

            print(f"[DEBUG] Все записи для user_id={user_id}:", all_rows)

            cursor.execute("SELECT topic, score FROM results WHERE user_id=?", (user_id,))
            rows = cursor.fetchall()

        if not rows:
            await message.answer("Вы ещё не отвечали ни на один вопрос.")
            return

        stats = {}
        total_score = 0

        for topic, score in rows:
            if topic not in stats:
                stats[topic] = {"count": 0, "total_score": 0}
            stats[topic]["count"] += 1
            stats[topic]["total_score"] += score
            total_score += score

        total_questions = len(rows)
        average_score = round(total_score / total_questions, 2)

        output = f"📊 Ваша статистика:\n"
        output += f"🔹 Всего вопросов: {total_questions}\n"
        output += f"🔹 Средний балл: {average_score}/10\n\n"
        output += "🔍 По темам:\n"

        for topic, data in stats.items():
            avg = round(data["total_score"] / data["count"], 2)
            output += f"• {TOPICS[topic][0]}: {data['count']} вопросов, средний балл — {avg}/10\n"

        await message.answer(output)


def register_quiz_handlers(quiz_router, quiz_game: QuizGame):
    '''Регистрирует все обработчики:'''

    @quiz_router.callback_query(F.data.in_(["quiz_prog", "quiz_math", "quiz_biology", "quiz_more"]))
    async def handle_quiz_callback(callback_query: CallbackQuery, state: FSMContext):
        '''Начать викторину по выбранной теме'''
        await quiz_game.handle_quiz_choice(callback_query, state, callback_query.data)

    @quiz_router.message(GPTStateRequests.quiz_game)
    async def process_answer(message: Message, state: FSMContext):
        '''Обработать ответ пользователя'''
        await quiz_game.evaluate_answer(message, state)

    @quiz_router.callback_query(F.data == "quiz_again")
    async def handle_again(callback_query: CallbackQuery, state: FSMContext):
        '''Еще один вопрос'''
        await callback_query.answer()

        data = await state.get_data()
        topic = data.get("topic")  # Тема остаётся, потому что мы её не удалили

        if not topic:
            await callback_query.message.answer("Сначала выберите тему.")
            return

        await quiz_game.handle_quiz_choice(callback_query, state, topic)

    @quiz_router.callback_query(F.data == "main_menu")
    async def handle_main_menu(callback_query: CallbackQuery, state: FSMContext):
        '''Вернуться в главное меню'''
        await callback_query.answer()  # Подтверждаем нажатие на кнопку

        await state.clear()

        photo = FSInputFile("resources/images/main.jpg")
        text_path = "resources/messages/main.txt"

        with open(text_path, "r", encoding="utf-8") as f:
            msg_text = f.read()
        buttons = ('/random', '/gpt', '/talk', '/quiz',)
        await callback_query.message.answer_photo(
            photo=photo,
            caption=msg_text,
            reply_markup=kb_replay(buttons)  # твоя клавиатура
        )

    @quiz_router.callback_query(F.data == "quiz_stats")
    async def handle_quiz_stats(callback_query: CallbackQuery, state: FSMContext):
        '''Посмотреть статистику'''
        await callback_query.answer()
        user_id = callback_query.from_user.id
        await quiz_game.show_stats(user_id, callback_query.message)
