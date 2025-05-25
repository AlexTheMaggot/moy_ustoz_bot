import asyncio
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from config import TELEGRAM_API_TOKEN
import kb
import db
import methods
from gsheet import google_sheets_sync

dp = Dispatcher(storage=MemoryStorage())


class Menu(StatesGroup):
    start = State()
    category_list = State()
    subcategory_list = State()
    teacher_list = State()
    change_lang = State()


@dp.message(CommandStart())
async def command_start_handler(message, state):
    text = ("🌟 Добро пожаловать в Мой Ustoz! Это бесплатный онлайн-гид по репетиторам 😊\n\n"
            "💚 Для учеников — подбор преподавателей за пару минут!\n"
            "💚 Для родителей — поиск идеального репетитора по оптимальной цене!\n\n"
            "Без комиссий и переплат!\nБыстро, удобно, информативно!\n\n"
            "---------------------------------------------------\n\n"
            "🌟 Moy Ustozga xush kelibsiz! Bu repetitorlar bo‘yicha bepul onlayn qo‘llanma 😊\n\n"
            "💚 O‘quvchilar uchun — o‘qituvchilarni bir necha daqiqada toping!\n"
            "💚 Ota-onalar uchun — maqbul narxda ideal repetitorni qidiring!\n\n"
            "Hech qanday komissiya va ortiqcha to‘lovlarsiz!\n"
            "Tez, qulay va foydali!\n\nTilni tanlang 👇\nВыберите язык 👇")
    user = await db.user_get(tg_user_id=message.chat.id)
    if not user:
        await db.create_data(table='users', tg_user_id=message.chat.id, date_added=int(time.time()))
    await state.set_state(Menu.start)
    await message.answer(text, reply_markup=kb.keyboard['start_kb'])


@dp.message(Menu.start)
async def menu_start_handler(message, state):
    if message.chat.id == 104566710:
        if message.photo:
            await message.answer(message.photo[-1].file_id)
        elif message.video:
            await message.answer(message.video.file_id)
    if message.text == kb.buttons['ru'].text:
        await state.update_data(lang='ru')
        await db.user_update(tg_user_id=message.chat.id, lang='ru')
        await state.set_state(Menu.category_list)
        text = "Отлично 👍\nВыберите раздел, который Вам нужен 👇"
        rm = await kb.category_list_kb(lang='ru')
    elif message.text == kb.buttons['uz'].text:
        await state.update_data(lang='uz')
        await db.user_update(tg_user_id=message.chat.id, lang='uz')
        await state.set_state(Menu.category_list)
        text = "Zo‘r 👍\nKerakli bo‘limni tanlang 👇"
        rm = await kb.category_list_kb(lang='uz')
    elif message.text == kb.buttons['i_am_teacher'].text:
        text = 'Отлично 👍 присоединяйтесь сюда👇\nAjoyib! Quyidagiga qo‘shilinglar👇\n@moy_ustoz_zayavki_bot'
        rm = kb.keyboard['start_kb']
    else:
        text = "Пожалуйста, выберите пункт ниже👇\n------------------------------\nQuyidagi elementni tanlang👇"
        rm = kb.keyboard['start_kb']
    await message.answer(text, reply_markup=rm)


@dp.message(Menu.category_list)
async def category_list_handler(message, state):
    data = await state.get_data()
    lang = await methods.get_lang(data, message.chat.id)
    category = await db.category_get(**{'name_' + lang: message.text})
    if category:
        await state.update_data(category_id=category['id'])
        subcategories = await db.subcategory_get(category_id=category['id'])
        teachers = await db.teacher_get(category_id=category['id'])
        if not subcategories and teachers:
            await state.update_data(teachers_from_cats=True)
            await state.set_state(Menu.teacher_list)
            await methods.teachers_sender(message, teachers, lang)
        else:
            if lang == 'ru':
                text = 'Супер ✅\nВыберите предмет, а мы подскажем классного учителя в этой категории 😉'
            else:
                text = ("Ajoyib ✅\nFan turini tanlang, biz esa sizga aynan "
                        "shu yo‘nalishda zo‘r ustozni tavsiya qilamiz 😉")
            rm = await kb.subcategory_list_kb(lang=lang, category_id=category['id'])
            await state.set_state(Menu.subcategory_list)
            await message.answer(text=text, reply_markup=rm)
    elif message.text == kb.buttons['change_lang_' + lang].text:
        await state.set_state(Menu.change_lang)
        if lang == 'ru':
            text = "Пожалуйста, укажите язык 👇"
        else:
            text = "Iltimos, tilni tanlang 👇"
        rm = kb.keyboard['change_lang_kb']
        await message.answer(text=text, reply_markup=rm)
    elif message.text == kb.buttons['i_am_teacher_' + lang].text:
        if lang == 'ru':
            text = text = 'Отлично 👍 присоединяйтесь сюда👇\n@moy_ustoz_zayavki_bot'
        else:
            text = text = 'Ajoyib! Quyidagiga qo‘shilinglar👇\n@moy_ustoz_zayavki_bot'
        rm = await kb.category_list_kb(lang=lang)
        await message.answer(text=text, reply_markup=rm)
    else:
        text = await methods.get_wrong_answer(lang)
        rm = await kb.category_list_kb(lang)
        await message.answer(text=text, reply_markup=rm)


@dp.message(Menu.subcategory_list)
async def subcategory_list_handler(message, state):
    data = await state.get_data()
    lang = await methods.get_lang(data, message.chat.id)
    subcategory = await db.subcategory_get(**{'name_' + lang: message.text})
    if subcategory:
        await state.update_data(teachers_from_cats=False)
        await state.update_data(subcategory_id=subcategory['id'])
        await state.set_state(Menu.teacher_list)
        teachers = await db.teacher_get(subcategory_id=subcategory['id'])
        await methods.teachers_sender(message, teachers, lang)
    elif message.text == kb.buttons['back_' + lang].text:
        await state.set_state(Menu.category_list)
        if lang == 'ru':
            text = "Отлично 👍\nВыберите раздел, который Вам нужен 👇"
        else:
            text = "Zo‘r 👍\nKerakli bo‘limni tanlang 👇"
        await message.answer(text=text, reply_markup=await kb.category_list_kb(lang))
    elif message.text == kb.buttons['change_lang_' + lang].text:
        await state.set_state(Menu.change_lang)
        if lang == 'ru':
            text = "Пожалуйста, укажите язык 👇"
        else:
            text = "Iltimos, tilni tanlang 👇"
        rm = kb.keyboard['change_lang_kb']
        await message.answer(text=text, reply_markup=rm)
    elif message.text == kb.buttons['i_am_teacher_' + lang].text:
        if lang == 'ru':
            text = text = 'Отлично 👍 присоединяйтесь сюда👇\n@moy_ustoz_zayavki_bot'
        else:
            text = text = 'Ajoyib! Quyidagiga qo‘shilinglar👇\n@moy_ustoz_zayavki_bot'
        rm = await kb.subcategory_list_kb(lang=lang, category_id=data['category_id'])
        await message.answer(text=text, reply_markup=rm)
    else:
        text = await methods.get_wrong_answer(lang)
        rm = await kb.subcategory_list_kb(lang, data['category_id'])
        await message.answer(text=text, reply_markup=rm)


@dp.message(Menu.teacher_list)
async def teacher_list_handler(message, state):
    data = await state.get_data()
    lang = await methods.get_lang(data, message.chat.id)
    if message.text == kb.buttons['only_female_' + lang].text:
        if data.get('teachers_from_cats'):
            teachers = await db.teacher_get(category_id=data['category_id'], only_female=True)
        else:
            teachers = await db.teacher_get(subcategory_id=data['subcategory_id'], only_female=True)
        await methods.teachers_sender(message, teachers, lang)
    elif message.text == kb.buttons['only_online_' + lang].text:
        if data.get('teachers_from_cats'):
            teachers = await db.teacher_get(category_id=data['category_id'], only_online=True)
        else:
            teachers = await db.teacher_get(subcategory_id=data['subcategory_id'], only_online=True)
        await methods.teachers_sender(message, teachers, lang)
    elif message.text == kb.buttons['price_sort_' + lang].text:
        if data.get('teachers_from_cats'):
            teachers = await db.teacher_get(category_id=data['category_id'], price_sort=True)
        else:
            teachers = await db.teacher_get(subcategory_id=data['subcategory_id'], price_sort=True)
        await methods.teachers_sender(message, teachers, lang)
    elif message.text == kb.buttons['back_' + lang].text:
        if data.get('teachers_from_cats'):
            await state.set_state(Menu.category_list)
            if lang == 'ru':
                text = "Отлично 👍\nВыберите раздел, который Вам нужен 👇"
            else:
                text = "Zo‘r 👍\nKerakli bo‘limni tanlang 👇"
            rm = await kb.category_list_kb(lang)
            await message.answer(text=text, reply_markup=rm)
        else:
            await state.set_state(Menu.subcategory_list)
            if lang == 'ru':
                text = "Супер ✅\nВыберите предмет, а мы подскажем классного учителя в этой категории 😉"
            else:
                text = ("Ajoyib ✅\nFan turini tanlang, biz esa sizga aynan "
                        "shu yo‘nalishda zo‘r ustozni tavsiya qilamiz 😉")
            rm = await kb.subcategory_list_kb(lang=lang, category_id=data['category_id'])
            await message.answer(text=text, reply_markup=rm)
    elif message.text == kb.buttons['i_am_teacher_' + lang].text:
        if lang == 'ru':
            text = text = 'Отлично 👍 присоединяйтесь сюда👇\n@moy_ustoz_zayavki_bot'
        else:
            text = text = 'Ajoyib! Quyidagiga qo‘shilinglar👇\n@moy_ustoz_zayavki_bot'
        rm = kb.keyboard['teachers_list_kb_' + lang]
        await message.answer(text=text, reply_markup=rm)
    else:
        text = await methods.get_wrong_answer(lang)
        rm = kb.keyboard['teacher_list_kb_' + lang]
        await message.answer(text=text, reply_markup=rm)


@dp.message(Menu.change_lang)
async def change_lang_handler(message: Message, state: FSMContext):
    if message.text == kb.buttons['ru'].text:
        await state.update_data(lang='ru')
        await db.user_update(tg_user_id=message.chat.id, lang='ru')
        await state.set_state(Menu.category_list)
        text = "Отлично 👍\nВыберите раздел, который Вам нужен 👇"
        rm = await kb.category_list_kb(lang='ru')
    elif message.text == kb.buttons['uz'].text:
        await state.update_data(lang='uz')
        await db.user_update(tg_user_id=message.chat.id, lang='uz')
        await state.set_state(Menu.category_list)
        text = "Zo‘r 👍\nKerakli bo‘limni tanlang 👇"
        rm = await kb.category_list_kb(lang='uz')
    elif message.text == kb.buttons['i_am_teacher'].text:
        text = 'Отлично 👍 присоединяйтесь сюда👇\nAjoyib! Quyidagiga qo‘shilinglar👇\n@moy_ustoz_zayavki_bot'
        rm = kb.keyboard['change_lang_kb']
    else:
        text = "Пожалуйста, выберите пункт ниже👇\n------------------------------\nQuyidagi elementni tanlang👇"
        rm = kb.keyboard['chabge_lang_kb']
    await message.answer(text, reply_markup=rm)


async def main():
    await db.init_db()
    bot = Bot(token=TELEGRAM_API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    sheets_task = asyncio.create_task(google_sheets_sync())
    try:
        await dp.start_polling(bot)
    finally:
        sheets_task.cancel()
        try:
            await sheets_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
