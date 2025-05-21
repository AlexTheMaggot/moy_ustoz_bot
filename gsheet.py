import asyncio

import gspread
from google.oauth2.service_account import Credentials

import db
from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


async def google_sheets_sync():
    async def data_creater(sheet, table, spreadsheet):
        data = spreadsheet.worksheet(sheet).get_all_records()
        for i in data:
            await db.create_data(table=table, name_ru=i['name_ru'], name_uz=i['name_uz'])

    while True:
        await db.wipe_data()
        credentials = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
        tables = [
            ['category', 'categories'],
            ['subcategory', 'subcategories'],
            ['format', 'formats'],
            ['status', 'statuses'],
            ['gender', 'genders'],
            ['language', 'languages'],
        ]
        for t in tables:
            await data_creater(sheet=t[0], table=t[1], spreadsheet=spreadsheet)
        data = spreadsheet.worksheet('new').get_all_records()
        n = 1
        for item in data:
            category = await db.category_get(name_ru=item['Категория'])
            if item['Подкатегория']:
                subcategory = await db.subcategory_get(name_ru=item['Подкатегория'])
                await db.update_data(table='subcategories', id=subcategory['id'], category_id=category['id'])
            status = await db.status_get(name_ru=item['Статус'])
            gender = await db.gender_get(name_ru=item['Пол'])
            formats = [await db.format_get(name_ru=i) for i in item['Формат занятий'].split(', ')]
            languages = [await db.language_get(name_ru=i) for i in item['Язык преподавания'].split(', ')]
            await db.create_data(table='teachers', id=n, name=item['ФИО'], price=item['Цена'],
                                 experience=item['Опыт работы'],
                                 location_ru=item['Локация (на русском)'], location_uz=item['Локация (на узбекском)'],
                                 gender_id=gender['id'],
                                 about_ru=item['О себе (на русском)'], about_uz=item['О себе (на узбекском)'],
                                 status_id=status['id'],
                                 education_ru=item['Образование (на русском)'],
                                 education_uz=item['Образование (на узбекском)'],
                                 tg_link=item["Кнопка 'написать'"], phone=item["Кнопка 'позвонить'"],
                                 photo_1=item['Фото1'],
                                 photo_2=item['Фото2'], photo_3=item['Фото3'], video=item['Видео'],
                                 category_id=category['id'],
                                 subcategory_id=subcategory['id'])
            for f in formats:
                await db.formats_teachers_create(teacher_id=n, format_id=f['id'])
            for l in languages:
                await db.languages_teachers_create(teacher_id=n, language_id=l['id'])
            n += 1
        print('Done')
        await asyncio.sleep(60 * 60)
