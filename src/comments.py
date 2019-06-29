import json

from webscraper import clean_up_html, get_page


def get_comment_api_url(note_id):
    return "https://www.salon24.pl/comments-api/comments?sourceId=Post-{}&limit=10000000".format(str(note_id))


def get_user_by_id_url(user_id):
    return "https://www.salon24.pl/komentator/{}".format(user_id)


def parse_comment_level(comments, comment_data):
    for comment_data_item in comment_data:
        deleted = comment_data_item['deleted']
        if deleted:
            continue
        original_id = comment_data_item['id']
        content = clean_up_html(comment_data_item['content'])
        user_id = int(comment_data_item['userId'])
        upvotes = comment_data_item['likes']
        downvotes = comment_data_item['dislikes']
        timestamp = int(comment_data_item['created']) / 1000

        parent_id = comment_data_item['parentId'] if 'parentId' in comment_data_item else None

        comments.append(dict(original_id=original_id,
                             content=content,
                             user_id=user_id,
                             upvotes=upvotes,
                             downvotes=downvotes,
                             parent_id=parent_id,
                             timestamp=timestamp))

        if 'comments' in comment_data_item:
            parse_comment_level(comments, comment_data_item['comments']['data'])


def parse_comments(note_id):
    comments = []

    response = get_page(get_comment_api_url(note_id))
    comment_json = response.content.decode()
    comment_json = json.loads(comment_json)

    if comment_json['error'] is None:
        comment_data = comment_json['data']['comments']['data']
        parse_comment_level(comments, comment_data)
    else:
        print("error: cannot load comment", note_id)

    return comments


def save_comments(db, c, scraper, comments, note_id, user_ids):
    for comment in comments:
        user_id = save_user(db, c, scraper, comment['user_id'], user_ids)
        save_comment(db, c, comment, note_id, user_id)


def save_user(db, c, scraper, user_id, user_ids):
    if user_id not in user_ids:
        user_url = get_user_by_id_url(user_id)
        r = scraper.prepare_soup_get_url(user_url)
        if r is not None:
            url, soup = r
            user_blog_info = scraper.parse_user_and_blog_info(soup)
            usr = user_blog_info['user']

            user_login = get_user_login(url)

            if usr['nick'] is None:
                return None

            c.execute(
                """INSERT INTO user (nick, about, about_long, 
                    facebook, twitter, google_plus, original_id, login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (usr['nick'], usr['about'], usr['about_long'],
                 usr['facebook'], usr['twitter'], usr['google_plus'], user_id, user_login)
            )
            db.commit()
            user_ids[user_id] = c.lastrowid
            return c.lastrowid
        else:
            return None
    else:
        return user_ids[user_id]


def get_user_login(url):
    if url[-1] == '/':
        user_login = url.rsplit('/', 2)[-2]
    else:
        user_login = url.rsplit(',', 1)[-1]
    if user_login.startswith("https://"):
        user_login = None
    return user_login


def save_comment(db, c, comment, note_id, user_id):
    c.execute(
        """INSERT IGNORE INTO comment (content, user_id, datetime, 
              upvotes, downvotes, note_id, original_id, parent_id)
        VALUES (%s, %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s)""",
        (comment['content'], user_id, comment['timestamp'],
         comment['upvotes'], comment['downvotes'], note_id,
         comment['original_id'], comment['parent_id'])
    )
