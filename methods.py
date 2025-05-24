from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder

import kb
import db


async def get_lang(data, tg_user_id):
    lang = data.get('lang')
    if not lang:
        user = await db.user_get(tg_user_id=tg_user_id)
        lang = user.get('lang')
    return lang


async def get_wrong_answer(lang):
    if lang == 'ru':
        text = "Пожалуйста, выберите пункт ниже👇"
    else:
        text = "Quyidagi elementni tanlang👇"
    return text


async def teachers_sender(message, teachers, lang):

    def formatted_year(y):
        if 11 <= y % 100 <= 14:
            suffix = 'лет'
        else:
            last_digit = y % 10
            if last_digit == 1:
                suffix = 'год'
            elif 2 <= last_digit <= 4:
                suffix = 'года'
            else:
                suffix = 'лет'
        return f'{y} {suffix}'

    for teacher in teachers:
        formatted_price = f'{teacher["price"]:,}'.replace(',', ' ')
        if lang == 'ru':
            text = f"<b>{teacher['name']}</b>\n💸 от {formatted_price} сум\n\n"
            text += '⭐️ ' + ', '.join([i["name_ru"] for i in teacher["formats"]]) + '\n'
            text += '⭐️ ' + teacher['status']['name_ru'] + '\n'
            text += f'⭐️ Опыт работы: {formatted_year(teacher["experience"])}\n'
            text += f'⭐️ Пол: {teacher["gender"]["name_ru"]}\n'
            text += f'⭐️ Язык(и) преподавания: {", ".join([i["name_ru"] for i in teacher["languages"]])}\n'
            text += f'📍 Локация: {teacher["location_ru"]}\n\n'
            text += f'<b>О себе:</b> {teacher["about_ru"]}\n\n'
            text += f'<b>Образование:</b> {teacher["education_ru"]}\n'
            text += f'<b>Номер телефона:</b> +{teacher["phone"]}'
            if teacher['tg_link']:
                inline_btn = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Написать', url=teacher['tg_link']),
                    ]
                ])
            else:
                inline_btn = None
        else:
            text = f"{teacher['name']}, {formatted_price} so‘mdan boshlab\n"
            text += ', '.join([i["name_uz"] for i in teacher["formats"]]) + '\n'
            text += teacher['status']['name_uz'] + '\n'
            text += f'Ish tajribasi: {teacher["experience"]} yil\n'
            text += f'Jinsi: {teacher["gender"]["name_uz"]}\n'
            text += f'Dars o‘tiladigan til: {", ".join([i["name_uz"] for i in teacher["languages"]])}\n'
            text += f'Manzil: {teacher["location_uz"]}\n\n'
            text += f'O‘zim haqimda: {teacher["about_uz"]}\n\n'
            text += f'Ma’lumoti: {teacher["education_uz"]}\n'
            text += f'Telefon raqami: +{teacher["phone"]}'
            if teacher['tg_link']:
                inline_btn = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Yozish', url=teacher['tg_link']),
                    ]
                ])
            else:
                inline_btn = None
        content = [
            ('photo_1', teacher.get('photo_1')),
            ('photo_2', teacher.get('photo_2')),
            ('photo_3', teacher.get('photo_3')),
            ('video', teacher.get('video'))
        ]
        content = [(k, v) for k, v in content if v]
        if len(content) > 1:
            media_group = MediaGroupBuilder(caption=text)
            for n, (k, v) in enumerate(content):
                if k == 'video':
                    media_group.add_video(media=v)
                else:
                    media_group.add_photo(media=v)
            await message.answer_media_group(media=media_group.build(), reply_markup=inline_btn, parse_mode='HTML')
        elif len(content) == 1:
            k, v = content[0]
            if k == 'video':
                await message.answer_video(video=v, caption=text, reply_markup=inline_btn)
            else:
                await message.answer_photo(photo=v, caption=text, reply_markup=inline_btn)
        else:
            await message.answer(text=text, reply_markup=inline_btn)
    if lang == 'ru':
        text = ('Чтобы связаться с преподавателем, нажмите на кнопку "Написать" '
                'под анкетой, или выберите пункт меню ниже 👇')
    else:
        text = ("""O'qituvchi bilan bog'lanish uchun forma ostidagi "Yozish" tugmasini """
                """bosing yoki quyidagi menyu bandini tanlang""")
    rm = kb.keyboard['teachers_list_kb_' + lang]
    await message.answer(text=text, reply_markup=rm)
