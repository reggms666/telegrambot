from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
import re

BOT_TOKEN = '7574195431:AAHYRUT_ovCnf4sm6q1Yh-ad1lLWJZ11TdU'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Базы данных слов
PROHIBITED_WORDS = {'мат', 'оскорбление', 'спам', 'реклама', 'сессия', 'универ', 'учеба'}
POSITIVE_WORDS = {'спасибо', 'пожалуйста', 'отлично', 'благодарю'}
QUESTION_WORDS = {'почему', 'как', 'когда', 'где'}

# Стартовая команда
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
        "Привет! Я Сигма Бот с фильтрами!\n"
        "Попробуй отправить мне:\n"
        "- Сообщение с плохими словами\n"
        "- Текст с цифрами\n"
        "- Вежливое сообщение\n"
        "- Вопрос",
        reply_markup=ReplyKeyboardRemove()
    )

# Команда помощи
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    help_text = (
        'Я эхо-бот с дополнительными функциями!\n'
        'Доступные команды:\n'
        '/start - начать общение\n'
        '/help - помощь\n'
        '/caps - преобразовать текст в верхний регистр\n'
        '/low - преобразовать текст в нижний регистр\n'
        '/reverse - перевернуть текст\n\n'
        'Фильтры автоматически реагируют на:\n'
        '- Запрещенные слова\n'
        '- Цифры в тексте\n'
        '- Вежливые слова\n'
        '- Вопросы'
    )
    await message.answer(help_text)

# Команда CAPS
@dp.message(Command(commands=['caps']))
async def process_caps_command(message: Message, command: CommandObject):
    if command.args:
        await message.answer(command.args.upper())
    else:
        await message.answer('Пожалуйста, укажите текст после команды /caps\nНапример: /caps привет')

# Команда LOW
@dp.message(Command(commands=['low']))
async def process_low_command(message: Message, command: CommandObject):
    if command.args:
        await message.answer(command.args.lower())
    else:
        await message.answer('Пожалуйста, укажите текст после команды /low\nНапример: /low ПРИВЕТ')

# Команда REVERSE
@dp.message(Command(commands=['reverse']))
async def process_reverse_command(message: Message, command: CommandObject):
    if command.args:
        await message.answer(command.args[::-1])
    else:
        await message.answer('Пожалуйста, укажите текст после команды /reverse\nНапример: /reverse текст')

# Обработка фото
@dp.message(F.photo)
async def send_photo(message: Message):
    if message.caption:
        # Проверяем подпись на плохие слова
        if any(word in message.caption.lower() for word in PROHIBITED_WORDS):
            await message.answer('⚠️ Подпись содержит недопустимые слова!')
            await message.delete()
        else:
            await message.reply_photo(
                message.photo[-1].file_id,
                caption=f'📸 Фото с подписью: "{message.caption}"'
            )
    else:
        await message.reply('📸 Красивое фото! Хотите добавить подпись?')

# 1. Фильтр нецензурной лексики (исправленный)
@dp.message(lambda message: any(word in message.text.lower() for word in PROHIBITED_WORDS))
async def filter_prohibited(message: Message):
    found_words = [word for word in PROHIBITED_WORDS if word in message.text.lower()]
    await message.reply(f"❌ Обнаружены запрещенные слова: {', '.join(found_words)}")
    await message.delete()

# 2. Фильтр цифр с подсветкой
@dp.message(F.text.regexp(r'\d'))
async def highlight_numbers(message: Message):
    highlighted = re.sub(r'(\d+)', r'<b>\1</b>', message.text)
    await message.reply(f"🔢 Найдены цифры:\n{highlighted}", parse_mode="HTML")

# 3. Фильтр положительных слов (исправленный)
@dp.message(lambda message: any(word in message.text.lower() for word in POSITIVE_WORDS))
async def praise_positive(message: Message):
    await message.reply("🌟 Респект за вежливость!")

# 4. Фильтр вопросов (исправленный)
@dp.message(lambda message: any(message.text.lower().startswith(word) for word in QUESTION_WORDS))
async def answer_questions(message: Message):
    await message.reply("🤔 Хороший вопрос! Я пока не знаю ответа.")

# 5. Фильтр ссылок
@dp.message(F.text.regexp(r'http[s]?://\S+'))
async def filter_links(message: Message):
    await message.reply("⛔ Ссылки запрещены!")
    await message.delete()

# 6. Фильтр длинных сообщений
@dp.message(lambda message: len(message.text) > 300)
async def filter_long_messages(message: Message):
    await message.reply("📏 Сообщение слишком длинное (макс. 300 символов)")

# Эхо-ответ для разрешенных сообщений
@dp.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)

if __name__ == '__main__':
    dp.run_polling(bot)