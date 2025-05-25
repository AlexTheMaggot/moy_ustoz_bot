from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import *

buttons = {
    'ru': KeyboardButton(text="🇷🇺 Русский"),
    'uz': KeyboardButton(text="🇺🇿 O'zbek"),
    'i_am_teacher': KeyboardButton(text="Я - репетитор/ Men - ustoz"),
    'i_am_teacher_ru': KeyboardButton(text="Я - репетитор"),
    'i_am_teacher_uz': KeyboardButton(text="Men - ustoz"),
    'back_ru': KeyboardButton(text='Назад'),
    'back_uz': KeyboardButton(text="Orqaga"),
    'change_lang_ru': KeyboardButton(text="Сменить язык"),
    'change_lang_uz': KeyboardButton(text="Tilni o'zgartirish"),
    'only_female_ru': KeyboardButton(text="Только женский пол"),
    'only_female_uz': KeyboardButton(text="Faqat ayolingizga yozilish"),
    'only_online_ru': KeyboardButton(text="Только онлайн"),
    'only_online_uz': KeyboardButton(text="Faqat online"),
    'price_sort_ru': KeyboardButton(text="Сортировать по возрастанию цены"),
    'price_sort_uz': KeyboardButton(text="Narxning o'sishi bo'yicha saralash"),
}

keyboard = {
    'start_kb': ReplyKeyboardMarkup(
        keyboard=[[buttons['ru'], buttons['uz']], [buttons['i_am_teacher']]],
        one_time_keyboard=True,
        resize_keyboard=True),
    'change_lang_kb': ReplyKeyboardMarkup(
        keyboard=[[buttons['ru'], buttons['uz']], [buttons['i_am_teacher']]],
        one_time_keyboard=True,
        resize_keyboard=True),
    'teachers_list_kb_ru': ReplyKeyboardMarkup(
        keyboard=[[buttons['only_female_ru']], [buttons['only_online_ru']], [buttons['price_sort_ru']],
                  [buttons['i_am_teacher_ru']], [buttons['back_ru']], ],
        one_time_keyboard=True,
        resize_keyboard=True),
    'teachers_list_kb_uz': ReplyKeyboardMarkup(
        keyboard=[[buttons['only_female_uz']], [buttons['only_online_uz']], [buttons['price_sort_uz']],
                  [buttons['i_am_teacher_uz']], [buttons['back_uz']], ],
        one_time_keyboard=True,
        resize_keyboard=True),
}


async def category_list_kb(lang):
    btn = []
    categories = await category_get()
    for category in categories:
        btn.append([KeyboardButton(text=category['name_' + lang])])
    btn.append([buttons['change_lang_' + lang]])
    btn.append([buttons['i_am_teacher_' + lang]])
    result = ReplyKeyboardMarkup(keyboard=btn, one_time_keyboard=True, resize_keyboard=True)
    return result


async def subcategory_list_kb(lang, category_id):
    btn = []
    subcategories = await subcategory_get(category_id=category_id)
    for subcategory in subcategories:
        btn.append([KeyboardButton(text=subcategory['name_' + lang])])
    btn.append([buttons['back_' + lang]])
    btn.append([buttons['change_lang_' + lang]])
    btn.append([buttons['i_am_teacher_' + lang]])
    result = ReplyKeyboardMarkup(keyboard=btn, one_time_keyboard=False, resize_keyboard=True)
    return result
