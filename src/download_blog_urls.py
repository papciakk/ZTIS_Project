import pickle

from webscraper import WebScraper


def run(start_page=1):
    all_blog_urls = []

    scraper = WebScraper()

    pages_number = scraper.get_pages_number()

    for page_no in range(start_page, pages_number + 1):
        blog_urls = scraper.get_blogs_from_page(page_no)
        all_blog_urls.extend(blog_urls)
        print("{}/{}".format(page_no, pages_number + 1))

    with open("blog_urls_all.dat", "wb") as f:
        pickle.dump(all_blog_urls, f)

    print(len(all_blog_urls))


if __name__ == '__main__':
    run(start_page=1)
