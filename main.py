import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

from aiogram import types
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F


from libretranslatepy import LibreTranslateAPI # API для перевода


load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_KEY') # использование токена из переменной окружения .env

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Список команд для меню
COMMANDS = [
    BotCommand(command='/start', description='Начало работы'),
    BotCommand(command='/help', description='Помощь'),
    BotCommand(command='/translate', description='Перевод текста'),
    BotCommand(command='/about', description='О боте')
]

# Определение состояний
class TranslationStates(StatesGroup):
    waiting_for_text = State()

# Установка команд меню при старте
async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(COMMANDS)


# Обработчик на команду /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    await message.answer(f"""Здравствуйте, {html.bold(message.from_user.full_name)}! Этот бот создан для того, чтобы помогать Вам быстро и просто находить перевод нужных Вам слов и словосочетаний с корейской языка на русский и наоборот.

Чтобы получить информацию о командах, нажмите /help

Чтобы начать переводить, нажмите /translate 

Чтобы получить более подробную информацию о боте, нажмите /about """)

# Обработчик на команду /help
@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:

    await message.answer("""В этом разделе содержится описание команд.
                         

Команда /start приветствует пользователя и предлагает воспользоваться другими командами.

После нажатия команды /translate Вы можете отправить слово или словосочетание на русском или корейском языке, бот сам определит язык и переведёт.

После нажатия команды /about Вам предоставляется информация о создателях ботах и о целях его создания.""")

# Обработчик команды /translate
@dp.message(Command("translate"))
async def start_translation(message: Message, state: FSMContext) -> None:
    await state.set_state(TranslationStates.waiting_for_text)
    await message.reply("Отправьте слово или словосочетание, которое хотите перевести")


@dp.message(TranslationStates.waiting_for_text)
async def command_translate_handler(message: Message, state: FSMContext) -> None:


    url_api = LibreTranslateAPI("http://localhost:5000")
        
    detected = url_api.detect(message.text)
    language = detected[0]['language'] if detected else None

    try:
        if language == "ru":
            translate_text = url_api.translate(message.text, "ru", "ko")
        elif language == "ko":
            translate_text = url_api.translate(message.text, "ko", "ru")
        else:
            translate_text = "Введи текст на русском или корейском языке"

        await message.reply(translate_text)

    except Exception as e:
        logging.error(f"Translation error: {e}")
        await message.reply("⚠️ Произошла ошибка при переводе. Попробуйте позже.")
    
    finally:
        await state.clear()


# Обработчик на команду /about
@dp.message(Command("about"))
async def command_about_handler(message: Message) -> None:

    await message.answer("""Данный Telegram-бот создали студенты 3-го курса группы 04.3-204 Института международных отношений, истории и востоковедения Казанского (Приволжского) Федерального университета Ибрагимова Раина, Иванова Виктория, Камалова Рената, Каречникова Лия, Саитова Вероника и Тимерзянова Алсу. 

Бот создан с целью защитить итоговый проект по программе «Цифровой переводчик / Постредактор PRO» и получить навыки программирования, которые сейчас востребованы." """)


# Запуск процесса поллинга новых апдейтов
async def main() -> None:
    await bot.set_my_commands(COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout) # Включаем логирование, чтобы не пропустить важные сообщения
    asyncio.run(main())