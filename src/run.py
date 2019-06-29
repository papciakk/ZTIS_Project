import pickle
import threading
from functools import partial
from multiprocessing.pool import Pool

import MySQLdb

import webscraper
from comments import parse_comments, save_comments
from db import save_user_data, save_blog_data, save_note_categories, save_note, save_note_category_link_table

threads_count = 10
blogs_urls_filename = "blog_urls_rest.dat"


def prepare():
    db = MySQLdb.connect(user="root",
                         db="salon24",
                         host="localhost",
                         password="1234",
                         charset="utf8")
    c = db.cursor()
    scraper = webscraper.WebScraper()
    return db, c, scraper


def scrap_comments(db, blog_note, c, note_id, scraper, user_ids):
    comments = parse_comments(blog_note['id'])
    save_comments(db, c, scraper, comments, note_id, user_ids)
    return comments


def scrap_note(blog_id, c, scraper, soup):
    blog_note = scraper.parse_blog_note(soup)
    category_ids = save_note_categories(c, blog_note['categories'])
    note_id = save_note(c, blog_note, blog_id)
    save_note_category_link_table(c, note_id, category_ids)
    return blog_note, note_id


def scrap_blog(partial_scraped_urls, user_ids, blog_url):
    thread_id = threading.current_thread().ident

    db, c, scraper = prepare()

    soup = scraper.prepare_soup(blog_url)
    if soup and scraper.blog_or_note_exists(soup):
        blog_notes_urls = scraper.get_blog_notes(soup)
        print("Scraping blog {} (thread: {}, notes: {})"
              .format(blog_url, thread_id, len(blog_notes_urls)))
        blog_stats = scraper.get_blog_stats(soup)
        user_blog_info = scraper.parse_user_and_blog_info(soup)

        user_login = get_user_login(blog_url)

        user_id = save_user_data(c, user_blog_info, user_login, user_ids)
        blog_id = save_blog_data(c, blog_stats, user_blog_info, user_id)

        start_note_id = 0 if blog_url not in partial_scraped_urls else partial_scraped_urls[blog_url]
        for i in range(start_note_id, len(blog_notes_urls)):
            blog_note_url = blog_notes_urls[i]

            print("Scraping note {}/{} (thread: {})"
                  .format(i + 1, len(blog_notes_urls), thread_id))
            soup = scraper.prepare_soup(blog_note_url['url'])
            if soup:
                if not scraper.blog_or_note_exists(soup):
                    continue
                blog_note, note_id = scrap_note(blog_id, c, scraper, soup)

                if blog_note_url['has_comments']:
                    scrap_comments(db, blog_note, c, note_id, scraper, user_ids)

                c.execute("""DELETE FROM scraped_urls WHERE url LIKE %s""", [blog_url])

                c.execute("""INSERT INTO scraped_urls (url, notes_saved) VALUES (%s, %s)""", [blog_url, i + 1])
                db.commit()
        db.commit()

    c.execute("""DELETE FROM scraped_urls WHERE url LIKE %s""", [blog_url])

    c.execute("""INSERT INTO scraped_urls (url) VALUES (%s)""", [blog_url])
    db.commit()


def get_user_login(blog_url):
    user_login = blog_url.rsplit('/', 2)[-2]
    return user_login


def run():
    db, c, scraper = prepare()

    with open(blogs_urls_filename, mode="rb") as f:
        blog_urls = pickle.load(f)

    c.execute("""SELECT url FROM scraped_urls WHERE notes_saved IS NULL""")
    scraped_urls = c.fetchall()
    scraped_urls = [u[0] for u in scraped_urls]

    filtered_blog_urls = [url for url in blog_urls if url not in scraped_urls]

    c.execute("""SELECT * FROM scraped_urls WHERE notes_saved IS NOT NULL""")
    partial_scraped_urls = c.fetchall()
    partial_scraped_urls = {u[0]: u[1] for u in partial_scraped_urls}

    c.execute("""SELECT id, original_id FROM user""")
    user_ids_r = c.fetchall()
    user_ids = {u[1]: u[0] for u in user_ids_r}

    c.execute("""SELECT count(*) FROM blog""")
    downloaded_blogs_cnt = c.fetchone()[0]

    print("Downloaded blogs:", downloaded_blogs_cnt)
    print("Blogs to download:", len(filtered_blog_urls))

    # scraped_blog_urls = []
    # with open("scraped_blog_urls.dat", mode="wb") as f:
    #     pickle.dump(scraped_blog_urls, f)

    scrap_blog_p = partial(scrap_blog, partial_scraped_urls, user_ids)

    with Pool(threads_count) as p:
        p.map(scrap_blog_p, filtered_blog_urls)

    # for url in filtered_blog_urls:
    # scrap_blog(partial_scraped_urls, user_ids, url)

    db.commit()
    db.close()


if __name__ == '__main__':
    run()
