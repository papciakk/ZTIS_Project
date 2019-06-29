from datetime import datetime

import html2text
import requests
from bs4 import BeautifulSoup


def clean_up_html(article_raw):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_tables = True
    text_maker.ignore_links = True
    text_maker.ignore_emphasis = True
    text_maker.single_line_break = True
    text_maker.ignore_images = True

    article = text_maker.handle(article_raw)
    return article


def get_page(url):
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }

    try:
        return requests.get(url, headers=headers, timeout=1000)
    except:
        print(url)
        return None


class WebScraper:

    @staticmethod
    def __is_good_response(page):
        if page is None:
            return None
        content_type = page.headers['Content-Type'].lower()
        return (page.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def get_pages_number(self):
        blogs_url = self.___get_blogs_url(0)

        response = get_page(blogs_url)
        if self.__is_good_response(response):
            soup = BeautifulSoup(response.content, "html.parser")

            return int(soup.select_one(".pager-page--last a").text)
        else:
            return None

    def get_blogs_from_page(self, page_no):
        blogs_url = self.___get_blogs_url(page_no)

        response = get_page(blogs_url)
        if self.__is_good_response(response):
            soup = BeautifulSoup(response.content, "html.parser")

            blog_list = soup.select("ul.blog-list li")

            return ["https://" + blog.find("a").attrs['href'][2:]
                    for blog in blog_list]

    @staticmethod
    def ___get_blogs_url(page_number):  # TODO: sortowanie od najstarszego
        return "https://www.salon24.pl/katalog-blogow/,alfabetycznie,{}".format(page_number)

    def get_blog_notes(self, soup):
        notes_raw = soup.select(".posts-list article")

        notes_urls = [dict(url="https://" + note.select_one("h2 a").attrs['href'][2:],
                           has_comments=note.select_one("footer .cloud-counter") is not None)
                      for note in notes_raw]

        next_page = soup.select_one(".pager .pager-page--next a")

        if next_page is not None:
            next_page_url = "https://" + next_page.attrs['href'][2:]
            next_page_soup = self.prepare_soup(next_page_url)

            if next_page_soup is not None:
                next_blog_note_urls = self.get_blog_notes(next_page_soup)
                notes_urls.extend(next_blog_note_urls)
            else:
                print(next_page_url)

        return notes_urls

    def prepare_soup(self, url):
        response = get_page(url)
        if self.__is_good_response(response):
            return BeautifulSoup(response.content, "html.parser")
        else:
            return None

    def prepare_soup_get_url(self, url):
        response = get_page(url)
        if self.__is_good_response(response):
            return response.url, BeautifulSoup(response.content, "html.parser")
        else:
            return None

    @staticmethod
    def get_blog_stats(soup):
        stats = soup.select(".user-header__counters div")
        followers_raw = stats[0]
        notes_raw = stats[1]
        views_raw = stats[2]

        followers = followers_raw.contents[2][:-1]
        followers = int(followers[:-1]) * 1000 if followers[-1] == 'k' else followers
        notes = notes_raw.contents[2][:-1]
        notes = int(notes[:-1]) * 1000 if notes[-1] == 'k' else notes
        views = views_raw.contents[2][:-1]
        views = int(views[:-1]) * 1000 if views[-1] == 'k' else views

        return dict(views=views,
                    notes=notes,
                    followers=followers)

    @staticmethod
    def parse_user_and_blog_info(soup):
        blog_name = soup.select_one("a.user-header__blog-name")
        blog_name = blog_name.text.strip() if blog_name is not None else ""
        blog_motto = soup.select_one(".user-header__blog-motto")
        blog_motto = blog_motto.text.strip() if blog_motto is not None else None
        blog_motto = None if blog_motto is not None and len(blog_motto) < 1 else blog_motto
        user_nick = soup.select_one(".user-header__user-nick a")
        user_nick = user_nick.text.strip() if user_nick is not None else ""
        user_nick = None if user_nick is not None and len(user_nick) < 1 else user_nick

        user_facebook = None
        user_twitter = None
        user_google_plus = None
        user_socials = soup.select(".user-header__socials a")
        for link in user_socials:
            if link is not None and len(link) >= 1:
                link = link.attrs['href']
                if "facebook" in link:
                    user_facebook = link
                elif "twitter" in link:
                    user_twitter = link
                elif "google" in link:
                    user_google_plus = link

        user_about = soup.select_one(".user-header__about")
        user_about = user_about.text.strip() if user_about is not None else None
        user_about = None if user_about is not None and len(user_about) < 1 else user_about
        user_about_long = soup.select_one(".user-about__content .too-high")
        user_about_long = user_about_long.text.strip() if user_about_long is not None else None
        user_about_long = None if user_about_long is not None and len(user_about_long) < 1 else user_about_long

        user_id_sel = soup.select_one(".user-header__buttons .button--clear")
        if user_id_sel is not None:
            user_id_raw = str(user_id_sel.attrs['onclick'])
            user_id = int(user_id_raw[user_id_raw.find("(") + 1:-1])
        else:
            user_id = None

        return dict(blog=dict(name=blog_name, motto=blog_motto),
                    user=dict(id=user_id, nick=user_nick,
                              facebook=user_facebook, twitter=user_twitter, google_plus=user_google_plus,
                              about=user_about, about_long=user_about_long))

    def parse_blog_note(self, soup):
        header = soup.select_one("article.article header")
        categories_raw = header.select_one(".category-breadcrumb")
        if categories_raw is None:
            categories = []
        else:
            categories = [a_tag.text
                          for a_tag in categories_raw.find_all("a")]

        views = header.select_one("span").text.strip()[:-7]
        datetime_raw = header.select_one("time").text.strip()
        if len(datetime_raw) == 0:
            datetime = '01 january 1977, 00:00'
        else:
            datetime = self.__convert_datetime(datetime_raw)
        name = header.select_one("h1").text.strip()
        article_raw = str(soup.select_one("article .article-content"))
        article = clean_up_html(article_raw)

        facebook_shares = soup.select_one(".article__socials .button--facebook span.button__badge")
        if facebook_shares:
            facebook_shares = facebook_shares.text.strip()
            facebook_shares = int(facebook_shares[:-1]) * 1000 if facebook_shares[-1] == 'k' else facebook_shares
        else:
            facebook_shares = 0

        note_id_raw = soup.select_one(".mod-user-post").attrs['data-set-as-read']
        note_id = int(note_id_raw[note_id_raw.find(":") + 1:])

        has_more_pages = soup.select_one(".pager-page--next")
        article_parts = ""
        while has_more_pages is not None:
            next_url = "https://" + has_more_pages.find("a").attrs["href"][2:]
            next_soup = self.prepare_soup(next_url)
            article_part_raw = str(next_soup.select_one("article .article-content"))
            article_part = clean_up_html(article_part_raw)
            article_parts += article_part

            has_more_pages = next_soup.select_one(".pager-page--next")

        article += article_parts

        return dict(id=note_id,
                    categories=categories,
                    views=views,
                    facebook_shares=facebook_shares,
                    datetime=datetime,
                    name=name,
                    content=article)

    def blog_or_note_exists(self, soup):
        return soup.select_one("header.user-header") is not None

    @staticmethod
    def __convert_datetime(d):
        d = d.replace("stycznia", "january")
        d = d.replace("lutego", "february")
        d = d.replace("marca", "march")
        d = d.replace("kwietnia", "april")
        d = d.replace("maja", "may")
        d = d.replace("czerwca", "june")
        d = d.replace("lipca", "july")
        d = d.replace("sierpnia", "august")
        d = d.replace("września", "september")
        d = d.replace("października", "october")
        d = d.replace("listopada", "november")
        d = d.replace("grudnia", "december")

        return datetime.strptime(d, '%d %B %Y, %H:%M')
