# -*- coding: utf-8 -*-
#####################################################################################################################
#                                                                                                                   #
# Парсер новостных разделов Ямальских СМИ.                                                                          #
#                                                                                                                   #
# MIT License                                                                                                       #
# Copyright (c) 2020 Michael Nikitenko                                                                              #
#                                                                                                                   #
#####################################################################################################################


from bs4 import BeautifulSoup
from db_engine import read_db, insert_db
import re
import requests

# Ссылки на страницы новостей
SP_URL = 'https://sever-press.ru/vse-novosti/'
AJAX_SP_URL = 'https://sever-press.ru/wp-admin/admin-ajax.php'
SP_QUERY = """a:63:{s:14:"posts_per_page";i:9;s:5:"error";s:0:"";s:1:"m";s:0:"";s:1:"p";
    i:0;s:11:"post_parent";s:0:"";s:7:"subpost";s:0:"";s:10:"subpost_id";s:0:"";s:10:"attachment";s:0:"";
    s:13:"attachment_id";i:0;s:4:"name";s:0:"";s:8:"pagename";s:0:"";s:7:"page_id";i:0;s:6:"second";s:0:"";
    s:6:"minute";s:0:"";s:4:"hour";s:0:"";s:3:"day";i:0;s:8:"monthnum";i:0;s:4:"year";i:0;s:1:"w";
    i:0;s:13:"category_name";s:0:"";s:3:"tag";s:0:"";s:3:"cat";s:0:"";s:6:"tag_id";s:0:"";s:6:"author";s:0:"";
    s:11:"author_name";s:0:"";s:4:"feed";s:0:"";s:2:"tb";s:0:"";s:5:"paged";i:0;s:8:"meta_key";s:0:"";
    s:10:"meta_value";s:0:"";s:7:"preview";s:0:"";s:1:"s";s:0:"";s:8:"sentence";s:0:"";s:5:"title";s:0:"";
    s:6:"fields";s:0:"";s:10:"menu_order";s:0:"";s:5:"embed";s:0:"";s:12:"category__in";a:0:{}s:16:"category__not_in";
    a:0:{}s:13:"category__and";a:0:{}s:8:"post__in";a:0:{}s:12:"post__not_in";a:0:{}s:13:"post_name__in";
    a:0:{}s:7:"tag__in";a:0:{}s:11:"tag__not_in";a:0:{}s:8:"tag__and";a:0:{}s:12:"tag_slug__in";
    a:0:{}s:13:"tag_slug__and";a:0:{}s:15:"post_parent__in";a:0:{}s:19:"post_parent__not_in";a:0:{}s:10:"author__in";
    a:0:{}s:14:"author__not_in";a:0:{}s:19:"ignore_sticky_posts";b:0;s:16:"suppress_filters";b:0;
    s:13:"cache_results";b:1;s:22:"update_post_term_cache";b:1;s:19:"lazy_load_term_meta";
    b:1;s:22:"update_post_meta_cache";b:1;s:9:"post_type";s:0:"";s:8:"nopaging";b:0;s:17:"comments_per_page";
    s:2:"50";s:13:"no_found_rows";b:0;s:5:"order";s:4:"DESC";}"""
KS_URL = 'https://ks-yanao.ru/novosti/'
KS_BASE_URL = "https://ks-yanao.ru/"
KS_PAGINATOR = '/?PAGEN_2='
YR_URL = 'https://yamal-region.tv/news/'
YR_BASE_URL = 'https://yamal-region.tv/'
YR_PAGINATOR = '/?page='


def filter(text: str) -> bool:
    """Поиск упоминания губернатора в тексте"""
    if re.search(r'\bгубернатор\b', text.lower()):
        return True
    elif re.search(r'\bартюхов\b', text.lower()):
        return True
    else:
        return False


def parse_all():
    """Запуск парсеров всех новостных сайтов"""
    parsed_data = parse_sp() + parse_ks() + parse_yr()
    print(f'parsed_data до бармицвы: {len(parsed_data)}')
    db_data = read_db()
    res = []
    for parse in parsed_data:
        status = False
        for db in db_data:
            if parse['url'] == db['url']:
                status = True
        if status == False:
            res.append(parse)
    print(f'parsed_data после бармицвы: {len(res)}')
    for row in res:
        insert_db(row)
    return res


def get_html(url: str) -> str:
    """Получает url и возвращает тело HTML документа в виде строки"""
    r = requests.get(url, headers={'User-Agent': 'Custom'})  # Создаем объект web-страницы по полученному url
    print(r, end="\n")  # Ответ от сервера <Response [200]>
    return r.text


def parse_sp():
    """Парсер сайте Север-Пресс"""
    print('parse SP')
    data = []
    for page in range(1, 10):
        try:
            parse_ajax = requests.post(url=AJAX_SP_URL, data={'action': 'loadarchive', 'query': SP_QUERY, 'page':
                page}).text.split('<div class="col-12 col-md-6 col-lg-4 article-container">')
            for i in range(1, len(parse_ajax)):
                title = parse_ajax[i].split('<h3>')[1].split('</h3>')[0].replace('\xa0', ' ')
                desc = ''
                img = parse_ajax[i].split('img src="')[1].split('"')[0]
                url = parse_ajax[i].split('href="')[1].split('"')[0]
                if filter(title):
                    print('MATCH SP!!!')
                    data.append({'title': title, 'description': desc, 'img': img, 'url': url})
        except:
            print('SP CONNECTION LOST!!!!!!!')
    return data


def parse_ks():
    """Парсер сайте Красный север"""
    print('parse KS')
    data = []
    for i in range(1, 10):
        try:
            html = get_html(KS_URL + KS_PAGINATOR + str(i))
            soup = BeautifulSoup(html, 'lxml')
            posts = soup.find_all('div', class_='content-body')
            for post in posts:
                title = post.find('a', class_='news-link text-none').get('title').strip().replace('\xa0', ' ')
                desc = post.find('p', class_='description font-open-s-light nm-b').text.strip().replace('\xa0', ' ')
                img = KS_BASE_URL + post.find('img').get('src')
                url = KS_BASE_URL + post.find('a', class_='news-link text-none').get('href')
                if filter(title):
                    data.append({'title': title, 'description': desc, 'img': img, 'url': url})
                elif filter(desc):
                    data.append({'title': title, 'description': desc, 'img': img, 'url': url})
        except:
            print('KS CONNECTION LOST!!!!!!!')
    return data


def parse_yr():
    """Парсер сайте Ямал-Регион"""
    print('parse YR')
    data = []
    for i in range(1, 10):
        try:
            html = get_html(YR_URL + YR_PAGINATOR + str(i))
            soup = BeautifulSoup(html, 'lxml')
            posts = soup.find_all('div', class_='news-row')
            for post in posts:
                title = post.find('div', class_='title').text.strip().replace('\xa0', ' ')
                desc = post.find('div', class_='text').text.strip().replace('\xa0', ' ')
                try:
                    img = YR_BASE_URL + post.find('img').get('src')
                except:
                    img = post.find('a', class_='video-tn').get('src')
                url = YR_BASE_URL + post.find('a').get('href')
                if filter(title):
                    data.append({'title': title, 'description': desc, 'img': img, 'url': url})
                elif filter(desc):
                    data.append({'title': title, 'description': desc, 'img': img, 'url': url})
        except:
            print('YR CONNECTION LOST!!!!!!!')
    return data


if __name__ == '__main__':
    for post in parse_sp():
        print(post)