from datetime import datetime


def save_note_category_link_table(c, note_id, category_ids):
    for category_id in category_ids:
        c.execute(
            """INSERT IGNORE INTO note_category (note_id, category_id) 
            VALUES (%s, %s)""", (note_id, category_id))


def save_note(c, blog_note, blog_id):
    c.execute(
        """INSERT IGNORE INTO note (original_id, name, content, datetime, facebook_shares, views, blog_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (blog_note['id'], blog_note['name'], blog_note['content'],
         blog_note['datetime'], blog_note['facebook_shares'], blog_note['views'],
         blog_id)
    )
    _id = c.lastrowid

    if _id == 0:
        c.execute("""SELECT id FROM note WHERE original_id = %s""", [blog_note['id']])
        duplicate_note_id = c.fetchone()
        return duplicate_note_id[0]
    else:
        return _id


def save_note_categories(c, categories):
    category_ids = []
    for category in categories:
        c.execute("""SELECT id FROM category WHERE name = %s""", [category])
        duplicate_cat_id = c.fetchone()

        if not duplicate_cat_id:
            c.execute("""INSERT INTO category (name) VALUES (%s)""", [category])
            category_ids.append(c.lastrowid)
        else:
            category_ids.append(duplicate_cat_id[0])
    return category_ids


def save_blog_data(c, blog_stats, user_blog_info, user_id):
    blog_info = user_blog_info['blog']

    c.execute("""SELECT id FROM blog WHERE name LIKE %s""", [blog_info['name']])
    duplicate_blog_id = c.fetchone()

    if not duplicate_blog_id:
        c.execute(
            """INSERT INTO blog (name, motto, views, notes, followers, user_id, downloaded)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (blog_info['name'], blog_info['motto'],
             blog_stats['views'], blog_stats['notes'], blog_stats['followers'],
             user_id, datetime.now())
        )
        return c.lastrowid
    else:
        return duplicate_blog_id[0]


def save_user_data(c, user_blog_info, user_login, user_ids):
    usr = user_blog_info['user']
    usr_original_id = usr['id']

    if usr_original_id not in user_ids:
        c.execute(
            """INSERT INTO user (nick, about, about_long, facebook, twitter, google_plus, original_id, login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (usr['nick'], usr['about'], usr['about_long'], usr['facebook'], usr['twitter'], usr['google_plus'],
             usr_original_id, user_login)
        )
        user_ids[usr_original_id] = c.lastrowid
        # print(len(user_ids))

    return user_ids[usr_original_id]
