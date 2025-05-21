import aiosqlite


db: aiosqlite.Connection = None


async def init_db():
    global db
    db = await aiosqlite.connect('db.sqlite3')


async def close_db():
    await db.close()


async def create_data(table, **kwargs):
    params = zip(kwargs.keys(), kwargs.values())
    params = [i for i in params if i[1] is not None]
    request = f'INSERT INTO "{table}" (' + ', '.join([i[0] for i in params]) + ') VALUES ('
    request += ', '.join(['?'] * len(params)) + ')'
    await db.execute(request, tuple(i[1] for i in params))
    await db.commit()


async def update_data(table, id, **kwargs):
    keys = []
    values = []
    request = f'UPDATE "{table}" SET '
    for k, v in kwargs.items():
        keys.append(k)
        values.append(v)
    request += ', '.join([f'{k} = ?' for k in keys])
    request += ' WHERE id = ?'
    values.append(id)
    await db.execute(request, tuple(values))
    await db.commit()


async def user_get(tg_user_id=None):
    if tg_user_id:
        async with db.execute("SELECT * FROM users WHERE tg_user_id=?", (tg_user_id, )) as cursor:
            user = await cursor.fetchone()
            if user:
                result = {'tg_user_id': user[0], 'lang': user[1], 'date': user[2]}
            else:
                result = []
    else:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            result = []
            for user in users:
                item = {'tg_user_id': user[0], 'lang': user[1], 'date': user[2]}
                result.append(item)
    return result


async def user_update(tg_user_id, lang):
    await db.execute("UPDATE users SET lang=? WHERE tg_user_id=?", (lang, tg_user_id))
    await db.commit()


async def user_delete(tg_user_id):
    await db.execute("DELETE FROM users WHERE tg_user_id=?", (tg_user_id, ))
    await db.commit()


async def category_create(name_ru, name_uz):
    await db.execute("INSERT INTO categories (name_ru, name_uz) VALUES (?, ?)", (name_ru, name_uz))
    await db.commit()


async def category_get(id=None, name_ru=None, name_uz=None):
    category = None
    categories = None
    if id:
        async with db.execute("SELECT * FROM categories WHERE id=?", (id, )) as cursor:
            category = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM categories WHERE name_ru=?", (name_ru, )) as cursor:
            category = await cursor.fetchone()
    elif name_uz:
        async with db.execute("SELECT * FROM categories WHERE name_uz=?", (name_uz, )) as cursor:
            category = await cursor.fetchone()
    else:
        async with db.execute("SELECT * FROM categories") as cursor:
            categories = await cursor.fetchall()
    if category:
        result = {'id': category[0], 'name_ru': category[1], 'name_uz': category[2]}
    elif categories:
        result = []
        for c in categories:
            item = {'id': c[0], 'name_ru': c[1], 'name_uz': c[2]}
            result.append(item)
    else:
        result = []
    return result


async def category_update(id, name_ru=None, name_uz=None):
    if name_uz or name_ru:
        req = ''
        if name_ru:
            req += f" name_ru='{name_ru}'"
        if name_uz:
            req += f"{',' if req else ''} name_uz='{name_uz}'"

        await db.execute("UPDATE categories SET ? WHERE id=?", (req, id))
        await db.commit()


async def category_delete(id):
    await db.execute("DELETE FROM categories WHERE id=?", (id, ))
    await db.commit()


async def subcategory_get(id=None, name_ru=None, name_uz=None, category_id=None):
    subcategory = None
    subcategories = None
    if id:
        async with db.execute("SELECT * FROM subcategories WHERE id=?", (id, )) as cursor:
            subcategory = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM subcategories WHERE name_ru=?", (name_ru, )) as cursor:
            subcategory = await cursor.fetchone()
    elif name_uz:
        async with db.execute("SELECT * FROM subcategories WHERE name_uz=?", (name_uz, )) as cursor:
            subcategory = await cursor.fetchone()
    elif category_id:
        async with db.execute("SELECT * FROM subcategories WHERE category_id=?", (category_id, )) as cursor:
            subcategories = await cursor.fetchall()
    else:
        async with db.execute("SELECT * FROM subcategories") as cursor:
            subcategories = await cursor.fetchall()
    if subcategory:
        result = {'id': subcategory[0], 'name_ru': subcategory[1], 'name_uz': subcategory[2],
                  'category_id': subcategory[3]}
    elif subcategories:
        result = []
        for s in subcategories:
            item = {'id': s[0], 'name_ru': s[1], 'name_uz': s[2], 'category_id': s[3]}
            result.append(item)
    else:
        result = []
    return result


async def subcategory_update(id, name_ru=None, name_uz=None, category_id=None):
    
    if name_uz or name_ru or category_id:
        req = ''
        if name_ru:
            req += f" name_ru='{name_ru}'"
        if name_uz:
            req += f"{',' if req else ''} name_uz='{name_uz}'"
        if category_id:
            req += f"{',' if req else ''} category_id='{category_id}'"

        await db.execute("UPDATE subcategories SET ? WHERE id=?", (req, id))
        await db.commit()


async def subcategory_delete(id):
    await db.execute("DELETE FROM subcategories WHERE id=?", (id, ))
    await db.commit()


async def status_get(id=None, name_ru=None):
    status = None
    statuses = None
    if id:
        async with db.execute("SELECT * FROM statuses WHERE id=?", (id, )) as cursor:
            status = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM statuses WHERE name_ru=?", (name_ru, )) as cursor:
            status = await cursor.fetchone()
    else:
        async with db.execute("SELECT * FROM statuses") as cursor:
            statuses = await cursor.fetchall()
    if status:
        result = {'id': status[0], 'name_ru': status[1], 'name_uz': status[2]}
    elif statuses:
        result = []
        for s in statuses:
            item = {'id': s[0], 'name_ru': s[1], 'name_uz': s[2]}
            result.append(item)
    else:
        result = []
    return result


async def gender_get(id=None, name_ru=None):
    gender = None
    genders = None
    if id:
        async with db.execute("SELECT * FROM genders WHERE id=?", (id, )) as cursor:
            gender = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM genders WHERE name_ru=?", (name_ru, )) as cursor:
            gender = await cursor.fetchone()
    else:
        async with db.execute("SELECT * FROM genders") as cursor:
            genders = await cursor.fetchall()
    if gender:
        result = {'id': gender[0], 'name_ru': gender[1], 'name_uz': gender[2]}
    elif genders:
        result = []
        for g in genders:
            item = {'id': g[0], 'name_ru': g[1], 'name_uz': g[2]}
            result.append(item)
    else:
        result = []
    return result


async def format_get(id=None, name_ru=None):
    format = None
    formats = None
    if id:
        async with db.execute("SELECT * FROM formats WHERE id=?", (id, )) as cursor:
            format = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM formats WHERE name_ru=?", (name_ru, )) as cursor:
            format = await cursor.fetchone()
    else:
        async with db.execute("SELECT * FROM formats") as cursor:
            formats = await cursor.fetchall()
    if format:
        result = {'id': format[0], 'name_ru': format[1], 'name_uz': format[2]}
    elif formats:
        result = []
        for f in formats:
            item = {'id': f[0], 'name_ru': f[1], 'name_uz': f[2]}
            result.append(item)
    else:
        result = []
    return result


async def language_get(id=None, name_ru=None):
    language = None
    languages = None
    if id:
        async with db.execute("SELECT * FROM languages WHERE id=?", (id, )) as cursor:
            language = await cursor.fetchone()
    elif name_ru:
        async with db.execute("SELECT * FROM languages WHERE name_ru=?", (name_ru, )) as cursor:
            language = await cursor.fetchone()
    else:
        async with db.execute("SELECT * FROM languages") as cursor:
            languages = await cursor.fetchall()
    if language:
        result = {'id': language[0], 'name_ru': language[1], 'name_uz': language[2]}
    elif languages:
        result = []
        for l in languages:
            item = {'id': l[0], 'name_ru': l[1], 'name_uz': l[2]}
            result.append(item)
    else:
        result = []
    return result


async def formats_teachers_create(format_id, teacher_id):
    await db.execute("INSERT INTO formats_teachers_id (format_id, teacher_id) VALUES (?, ?)", (format_id, teacher_id))
    await db.commit()


async def languages_teachers_create(language_id, teacher_id):
    await db.execute("INSERT INTO languages_teachers_id (language_id, teacher_id) VALUES (?, ?)",
                     (language_id, teacher_id))
    await db.commit()


async def teacher_get(category_id=None, subcategory_id=None, only_female=None, only_online=None, price_sort=None):

    def make_dict(data):

        def make_joined(d_i, prefix):
            return {'id': d_i[f'{prefix}_id'], 'name_ru': d_i[f'{prefix}_name_ru'],
                    'name_uz': d_i[f'{prefix}_name_uz']}

        out = {
            'id': data['id'],
            'category': make_joined(data, 'category'),
            'subcategory': make_joined(data, 'subcategory'),
            'status': make_joined(data, 'status'),
            'gender': make_joined(data, 'gender'),
            'formats': [
                {'id': f_id, 'name_ru': f_ru, 'name_uz': f_uz}
                for f_id, f_ru, f_uz in zip(
                    data['formats_id'].split(','),
                    data['formats_ru'].split(','),
                    data['formats_uz'].split(','))
            ] if data['formats_id'] else [],
            'languages': [
                {'id': l_id, 'name_ru': l_ru, 'name_uz': l_uz}
                for l_id, l_ru, l_uz in zip(
                    data['languages_id'].split(','),
                    data['languages_ru'].split(','),
                    data['languages_uz'].split(','))
            ] if data['languages_id'] else [],
            'education_ru': data['education_ru'],
            'education_uz': data['education_uz'],
            'location_ru': data['location_ru'],
            'location_uz': data['location_uz'],
            'about_ru': data['about_ru'],
            'about_uz': data['about_uz'],
            'photo_1': data['photo_1'],
            'photo_2': data['photo_2'],
            'photo_3': data['photo_3'],
            'video': data['video'],
            'tg_link': data['tg_link'],
            'phone': data['phone'],
            'experience': data['experience'],
            'name': data['name'],
            'price': data['price']
        }
        return out

    async def make_output(curs):
        cols = [col[0] for col in curs.description]
        result = []
        for item in await curs.fetchall():
            data_item = dict(zip(cols, item))
            teacher = make_dict(data_item)
            result.append(teacher)
        return result

    db_request = ("SELECT teachers.id, "
                  "GROUP_CONCAT(DISTINCT formats.id) AS formats_id, "
                  "GROUP_CONCAT(DISTINCT formats.name_ru) AS formats_ru, "
                  "GROUP_CONCAT(DISTINCT formats.name_uz) AS formats_uz, "
                  "GROUP_CONCAT(DISTINCT languages.id) AS languages_id, "
                  "GROUP_CONCAT(DISTINCT languages.name_ru) AS languages_ru, "
                  "GROUP_CONCAT(DISTINCT languages.name_uz) AS languages_uz, "
                  "categories.id AS category_id, categories.name_ru AS category_name_ru, "
                  "categories.name_uz AS category_name_uz, subcategories.id AS subcategory_id, "
                  "subcategories.name_ru AS subcategory_name_ru, subcategories.name_uz AS subcategory_name_uz, "
                  "teachers.name, teachers.price, statuses.id AS status_id, statuses.name_ru AS status_name_ru, "
                  "statuses.name_uz AS status_name_uz, teachers.experience, genders.id AS gender_id, "
                  "genders.name_ru AS gender_name_ru, genders.name_uz AS gender_name_uz, teachers.location_ru, "
                  "teachers.location_uz, teachers.about_ru, teachers.about_uz, teachers.education_ru, "
                  "teachers.education_uz, teachers.tg_link, teachers.phone, teachers.photo_1, teachers.photo_2, "
                  "teachers.photo_3, teachers.video "
                  "FROM teachers "
                  "LEFT JOIN categories ON categories.id=teachers.category_id "
                  "LEFT JOIN subcategories ON subcategories.id=teachers.subcategory_id "
                  "LEFT JOIN statuses ON statuses.id=teachers.status_id "
                  "LEFT JOIN genders ON genders.id=teachers.gender_id "
                  "LEFT JOIN formats_teachers_id ON formats_teachers_id.teacher_id = teachers.id "
                  "LEFT JOIN formats ON formats.id = formats_teachers_id.format_id "
                  "LEFT JOIN languages_teachers_id ON languages_teachers_id.teacher_id = teachers.id "
                  "LEFT JOIN languages ON languages.id = languages_teachers_id.language_id")
    params = {
        'teachers.category_id': category_id,
        'teachers.subcategory_id': subcategory_id,
        'teachers.gender_id': 2 if only_female else None,
        'formats_teachers_id.format_id': 1 if only_online else None
    }
    params = {k: v for k, v in params.items() if v is not None}
    if params:
        conditions = []
        values = []
        for k, v in params.items():
            conditions.append(f"{k} = ?")
            values.append(v)
        db_params = tuple(values)
        db_request += " WHERE " + ' AND '.join(conditions)
    else:
        db_params = None
        
    db_request += "GROUP BY teachers.id"
    if price_sort:
        db_request += " ORDER BY price ASC"
    async with db.execute(db_request, db_params) as cursor:
        return await make_output(cursor)


async def wipe_data():
    await db.execute('DELETE FROM formats_teachers_id;')
    await db.execute('DELETE FROM languages_teachers_id;')
    await db.execute('DELETE FROM teachers;')
    await db.execute('DELETE FROM formats;')
    await db.execute('DELETE FROM genders;')
    await db.execute('DELETE FROM languages;')
    await db.execute('DELETE FROM statuses;')
    await db.execute('DELETE FROM subcategories;')
    await db.execute('DELETE FROM categories;')
    await db.execute("DELETE FROM sqlite_sequence WHERE name='formats_teachers_id';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='languages_teachers_id';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='teachers';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='formats';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='genders';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='languages';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='statuses';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='subcategories';")
    await db.execute("DELETE FROM sqlite_sequence WHERE name='categories';")
    await db.commit()
