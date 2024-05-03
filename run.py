import re
from typing import Optional
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt') 
from fastapi import FastAPI,Request,Query
from fastapi.responses import RedirectResponse
from urllib.parse import unquote


def analyze_title(url, keyword):
    # Загрузка страницы
    response = requests.get(url)
    if response.status_code != 200:
        return "Ошибка: Невозможно загрузить страницу"
    
    load_time = response.elapsed.total_seconds()
    page_size = len(response.content)
    page_size_kb = page_size / 1024

    soup = BeautifulSoup(response.text, 'html.parser')

    # Проверка тега Title
    title_tag = soup.title.string if soup.title else ""
    title_present = True if title_tag else False
    title_contains_keyword = True if keyword.lower() in title_tag.lower() else False
    title_length = len(title_tag)
    numbers_in_title = bool(re.search(r'\d', title_tag))
    
    
    # Проверка тега Title
    meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    
    
    if meta_keywords_tag:
        keywords_content = meta_keywords_tag.get('content', '')
        keywords_list = [word.strip() for word in keywords_content.split(',') if word.strip()]
        keywords_present = True if keywords_list else False
        keywords_contains_keyword = True if keyword.lower() in keywords_content.lower() else False
        keywords_count = len(keywords_list)
        keywords_length = len(keywords_content)
    else:
        keywords_present = False
        keywords_contains_keyword = False
        keywords_count = 0
        keywords_length = 0
    
    # Поиск тега Description
    meta_description_tag = soup.find('meta', attrs={'name': 'description'})

    if meta_description_tag:
        description_content = meta_description_tag.get('content', '')
        description_present = True if description_content else False
        description_contains_keyword = True if keyword.lower() in description_content.lower() else False
        description_length = len(description_content)
    else:
        description_present = False
        description_contains_keyword = False
        description_length = 0

    # Поиск тега <html> и значения атрибута lang
    html_tag = soup.find('html')
    if html_tag:
        lang_attribute = html_tag.get('lang', '')
        if lang_attribute:
            lang_attribute=lang_attribute
        else:
            lang_attribute="Ошибка: Не удалось определить язык страницы"

     # Поиск тега <meta> с атрибутом charset
    charset_meta_tag = soup.find('meta', charset=True)
    if charset_meta_tag:
        charset = charset_meta_tag.get('charset', '').lower()
        if charset == 'utf-8':
            charset="Charset: UTF-8"
        else:
            charset=f"Charset: {charset}, необходимо использовать UTF-8"
    else:
        charset="Ошибка: Не найден тег <meta> с атрибутом charset"


    # Поиск тега <article>
    article_tag = soup.find('article')
    
    if article_tag:
        # Проверяем, содержится ли весь контент внутри тега <article>
        all_content_inside_article = all(content.find_parents('article') for content in soup.find_all(True, recursive=False))
        
        if all_content_inside_article:
            article_tag="Тег <article> присутствует на странице, и весь контент находится внутри него."
        else:
            article_tag="Тег <article> присутствует на странице, но не весь контент находится внутри него."
    else:
        article_tag="Тег <article> не найден на странице."

    

     # Поиск тега <h1>
    h1_tags = soup.find_all('h1')
    
    if h1_tags:
        # Проверка вхождения точной ключевой фразы в тег <h1>
        keyword_in_h1 = any(keyword.lower() in h1_tag.text.lower() for h1_tag in h1_tags)
        
        # Проверка отсутствия точного совпадения с <title>
        title_tag = soup.title.string if soup.title else ""
        exact_match_with_title = any(h1_tag.text.lower() == title_tag.lower() for h1_tag in h1_tags)
        
        H1_present = True,
        Keyword_found_in_H1=keyword_in_h1,
        Exact_match_with_Title=not exact_match_with_title
    else:
        H1_present =False,
        Keyword_found_in_H1 =False,
        Exact_match_with_Title= False
        


     # Поиск всех тегов <h2>
    h2_tags = soup.find_all('h2')

    if len(h2_tags) >= 2:
        # Проверка наличия как минимум 2х подзаголовков <h2>
        keyword_found = False
        for h2_tag in h2_tags:
            if keyword.lower() in h2_tag.text.lower():
                keyword_found = True
                break

        
        At_least_2_H2_tags_present=True,
        Keyword_found_in_at_least_one_H2_tag=keyword_found
        
    else:
        At_least_2_H2_tags_present=True,
        Keyword_found_in_at_least_one_H2_tag=False


    
     # Поиск всех тегов <h2>
    h2_tags = soup.find_all('h2')

    if h2_tags:
        # Поиск первого тега <h2>
        first_h2_tag = h2_tags[0]

        # Поиск предыдущих элементов перед первым тегом <h2>
        prev_elements = []
        prev_element = first_h2_tag.find_previous_sibling()
        while prev_element:
            prev_elements.insert(0, prev_element)
            prev_element = prev_element.find_previous_sibling()

        # Проверка наличия маркированного или немаркированного списка перед первым тегом <h2>
        toc_found = False
        for element in prev_elements:
            if element.name == 'ul' or element.name == 'ol':
                toc_found = True
                break

        if toc_found:
            # Проверка наличия уникальных ID для всех тегов <h2>
            for h2_tag in h2_tags:
                if not h2_tag.get('id'):
                    TOC_present=False,
                    All_H2_tags_should_have_unique_IDs=False


                TOC_present=True,
                All_H2_tags_should_have_unique_IDs=True
            
        else:
            TOC_present=True,
            All_H2_tags_should_have_unique_IDs=True
    else:
        TOC_present=True,
        All_H2_tags_should_have_unique_IDs=True
    
    
#     iframe_tags = soup.find_all('iframe')
# # Если тег <iframe> отсутствует, возвращаем True
#     if not iframe_tags:
#         print('Тег Iframe отсутствует')
#     else:
#         print('Тег Iframe присутствует')
    
#     object_tags = soup.find_all('object', type="application/x-shockwave-flash")
#     if not object_tags:
#         print('Тег object_tags отсутствует')
#     else:
#         print('Тег object_tags присутствует')
    
#     favicon_link_tag = soup.find('link', rel="icon")
#     if favicon_link_tag:
#         favicon_type = favicon_link_tag.get('type', '').lower()
#         if 'svg' in favicon_type:
#             print("Иконка favicon присутствует на странице и представлена в формате SVG.")
#         else:
#             print("Иконка favicon присутствует на странице, но не в формате SVG.")
#     else:
#         print("Иконка favicon отсутствует на странице.")
    
#     script_tags = soup.find_all('script')
#     bottom_scripts_count = len([script_tag for script_tag in script_tags if not script_tag.find_next_sibling()])
#     total_scripts_count = len(script_tags)
#     if bottom_scripts_count == total_scripts_count:
#         print("Все теги <script> расположены внизу страницы.")
#     else:
#         print("Не все теги <script> расположены внизу страницы.")

#     yandex_metrica_script = soup.find('script', text=lambda text: text and 'yandex.metrika' in text.lower())
#     google_analytics_script = soup.find('script', text=lambda text: text and 'google-analytics' in text.lower())
#     vk_pixel_script = soup.find('script', text=lambda text: text and 'vk.com/rtrg' in text.lower())

#     results = {}

#     results['Яндекс Метрика'] = bool(yandex_metrica_script)
#     results['Google Analytics'] = bool(google_analytics_script)
#     results['VK pixel'] = bool(vk_pixel_script)

#     print(results)



#     # Список CRM-скриптов для проверки
#     crm_scripts = {
#         "Битрикс24": "bitrix24.ru",
#         "AmoCRM": "amocrm.com"
#     }
            
#     # Проверяем наличие каждого CRM-скрипта на странице
#     presence_results = {}
#     for crm_name, crm_src in crm_scripts.items():
#         script_tag = soup.find('script', src=lambda s: s and crm_src in s)
#         presence_results[crm_name] = bool(script_tag)
            
#     print(presence_results)



#     # Список CMS-скриптов для проверки
#     cms_scripts = {
#         "WordPress": "/wp-content/",
#         "Tilda": "tilda.ws",
#         "1C-Bitrix": "bitrix"
#         }
            
#     # Проверяем наличие каждого CMS-скрипта на странице
#     presence_results = {}
#     for cms_name, cms_src in cms_scripts.items():
#         script_tag = soup.find('script', src=lambda s: s and cms_src in s)
#         presence_results[cms_name] = bool(script_tag)
            
#     print(presence_results)


# # Поиск тега <meta> с атрибутом name="keywords"
#     keywords_meta_tag = soup.find('meta', attrs={'name': 'keywords'})    
#     if keywords_meta_tag:
# # Получаем содержимое атрибута content
#         keywords_content = keywords_meta_tag.get('content')
# # Разделяем ключевые фразы и возвращаем список
#         keywords_list = keywords_content.split(',')
#         print(keywords_list)
#     else:
#         print("На странице не найдены ключевые фразы")


    # open_graph_meta_tags = soup.find_all('meta', attrs={'property': lambda p: p and p.startswith('og:')})
    # if open_graph_meta_tags:
    #     og_title_meta_tag = soup.find('meta', property='og:title').get('content')
    #     if og_title_meta_tag:
    #          print(f"Заголовок страницы в микроразметке Open Graph заполнен.")
    #     else:
    #         print("Заголовок страницы отсутствует в микроразметке Open Graph.")
    
    #     og_description_meta_tag = soup.find('meta', property='og:description')
    #     if og_description_meta_tag:
    #         description_text = og_description_meta_tag.get('content')
    #         print(description_text)
    #     else:
    #         print("Краткое описание страницы в микроразметке Open Graph не найдено.")

    #     og_url_meta_tag = soup.find('meta', property='og:url')
    #     if og_url_meta_tag:
    #         # Извлекаем URL из атрибута content
    #         url_text = og_url_meta_tag.get('content')
    #         print(url_text)
    #     else:
    #         print("URL страницы в микроразметке Open Graph не найден.")
    
    #     og_type_meta_tag = soup.find('meta', property='og:type')
    #     if og_type_meta_tag:
    #         # Извлекаем тип контента из атрибута content
    #         type_text = og_type_meta_tag.get('content')
    #         print(type_text)
    #     else:
    #         print("Тип контента в микроразметке Open Graph не найден.")
        
    #     og_image_meta_tag = soup.find('meta', property='og:image')
    #     if og_image_meta_tag:
    #         # Извлекаем URL изображения из атрибута content
    #         image_url = og_image_meta_tag.get('content')
    #         print(image_url)
    #     else:
    #         print("Изображение, связанное с контентом, в микроразметке Open Graph не найдено.")

    #     og_site_name_meta_tag = soup.find('meta', property='og:site_name')
    #     if og_site_name_meta_tag:
    #         # Извлекаем название сайта из атрибута content
    #         site_name = og_site_name_meta_tag.get('content')
    #         print(site_name)
    #     else:
    #         print("Название сайта в микроразметке Open Graph не найдено.")
    #     og_action_meta_tag = soup.find('meta', property='og:action')
    #     if og_action_meta_tag:
    #         print("Действие пользователя присутствует в микроразметке Open Graph.")
    #     else:
    #         print("Действие пользователя в микроразметке Open Graph не найдено.")
        
    #     og_property_meta_tag = soup.find('meta', property='og:property')
    #     if og_property_meta_tag:
    #         print("Атрибут или свойство объекта присутствует в микроразметке Open Graph.")
    #     else:
    #         print("Атрибут или свойство объекта в микроразметке Open Graph не найдено.")
        
    #     og_event_meta_tag = soup.find('meta', property='og:event')
    #     if og_event_meta_tag:
    #         print("Мероприятие или событие присутствует в микроразметке Open Graph.")
    #     else:
    #         print("Мероприятие или событие в микроразметке Open Graph не найдено.")
        
    #     # Находим все теги <img> на странице
    #     images = soup.find_all('img')
    #     # Инициализируем переменные для подсчета символов и изображений
    #     total_characters = 0
    #     total_images = len(images)
    #     alt_keyword_count = 0

    #     # Проходимся по каждому тегу <img>
    #     for img in images:
    #         # Проверяем атрибут ALT
    #         alt = img.get('alt', '').lower()
    #         if alt:
    #             total_characters += len(alt)
    #             # Проверяем наличие точной ключевой фразы в атрибуте ALT
    #             if re.search(rf'\b{keyword}\b', alt, re.IGNORECASE):
    #                 alt_keyword_count += 1
            
    #         # Проверяем формат изображения
    #         src =img.get('src', '').lower()
    #         print(src)
            
    #         if src.endswith(('webp', 'jpg', 'jpeg', 'png')):
    #             # Проверяем размер изображения
    #             image_size = requests.head(src).headers.get('content-length')
    #             if image_size:
    #                 image_size_kb = int(image_size) / 1024
    #                 if image_size_kb <= 100:
    #                     # Получаем размер изображения в пикселях
    #                     width = img.get('width', '')
    #                     height = img.get('height', '')
    #                     if width and height:
    #                         # Проверяем размер изображения
    #                         if int(width) <= 100 and int(height) <= 100:
    #                             total_characters += image_size_kb
    #                         else:
    #                             print("Ошибка: Размер изображения превышает 100x100 пикселей.") 
    #                     else:
    #                         print("Ошибка: Не удалось получить размер изображения.")
    #                 else:
    #                     print("Ошибка: Вес изображения превышает 100 кб.") 
    #             else:
    #                 print("Ошибка: Не удалось получить размер изображения.") 
    #         else:
    #             print("Ошибка: Недопустимый формат изображения.") 
        
    #     if total_characters >= 3000:
    #         print(f"На странице найдено {total_images} изображений, атрибут ALT заполнен для всех изображений, включая точную ключевую фразу в ALT как минимум для одного изображения.") 
    #     else:
    #         print("Ошибка: Недостаточное количество символов на странице для обработки изображений.") 





    #     # Находим все элементы <p> на странице
    #     paragraphs = soup.find_all('p')
    #     # Инициализируем переменные для общей длины всех элементов <p>,
    #     # количества элементов <p> без разделения и общего количества точных и неточных вхождений
    #     total_length = 0
    #     consecutive_paragraphs = 0
    #     exact_occurrences = 0
    #     inexact_occurrences = 0


    #     # Проходимся по каждому элементу <p>
    #     for paragraph in paragraphs:
    #         # Получаем текст элемента <p>
    #         p_text = paragraph.get_text()
    #         # Проверяем точное вхождение ключевой фразы в начале или середине первого предложения
    #         if re.search(rf'\b{keyword}\b', p_text[:len(keyword)*2], re.IGNORECASE):
    #             exact_occurrences += 1
    #         # Проверяем точное вхождение ключевой фразы не менее одного раза на 1.000 символов
    #         exact_occurrences += len(re.findall(rf'\b{keyword}\b', p_text, re.IGNORECASE))
    #         # Проверяем неточное вхождение ключевой фразы не менее одного раза на 1.000 символов дополнительно
    #         inexact_occurrences += len(re.findall(rf'{keyword}', p_text, re.IGNORECASE))
    #         # Проверяем длину элемента <p>
    #         total_length += len(p_text)
    #         # Проверяем количество идущих подряд элементов <p> без разделения
    #         if paragraph.find_next_sibling('p'):
    #             consecutive_paragraphs += 1
    #         else:
    #             consecutive_paragraphs = 0
    #     # Рассчитываем равномерность распределения точных и неточных ключевых фраз по всем элементам <p>
    #     total_paragraphs = len(paragraphs)
    #     uniformity = (exact_occurrences + inexact_occurrences) / (total_paragraphs * 2)
    #     p_Open_Graph={
    #             "Total Paragraphs": total_paragraphs,
    #             "Total Length": total_length,
    #             "Consecutive Paragraphs": consecutive_paragraphs,
    #             "Exact Occurrences": exact_occurrences,
    #             "Inexact Occurrences": inexact_occurrences,
    #             "Uniformity": uniformity
    #         }


    #     print(p_Open_Graph)
    
    #     paragraphs = soup.find_all(['p', 'article'])

    #     # Переменная для хранения результатов проверки
    #     lists_between_paragraphs = False
    #     tables_between_paragraphs = False

    #     # Проходимся по каждому элементу <p> и <article>
    #     for item in paragraphs:
    #         # Проверяем наличие элементов <ul> или <ol> между параграфами <p>
    #         for sibling in item.find_next_siblings():
    #             if sibling.name in ['ul', 'ol']:
    #                 lists_between_paragraphs = True
    #                 break
    #         # Проверяем наличие элементов <ul> или <ol> внутри тега <article>
    #         for child in item.find_all(['ul', 'ol']):
    #             if child.parent.name == 'article':
    #                 lists_between_paragraphs = True
    #                 break
    #     if lists_between_paragraphs:
    #         print("Списки между параграфами <p> или внутри тега <article> присутствуют на странице.")
    #     else:
    #         print("Списки между параграфами <p> или внутри тега <article> отсутствуют на странице.")
        
    #     for item in paragraphs:
    #         # Проверяем наличие элементов <ul> или <ol> между параграфами <p>
    #         for sibling in item.find_next_siblings():
    #             if sibling.name == 'table':
    #                 lists_between_paragraphs = True
    #                 break
    #         # Проверяем наличие элементов <ul> или <ol> внутри тега <article>
    #         for child in item.find_all('table'):
    #             if child.parent.name == 'article':
    #                 lists_between_paragraphs = True
    #                 break
    #     if tables_between_paragraphs:
    #         print("Таблицы между параграфами <p> или внутри тега <article> присутствуют на странице.")
    #     else:
    #         print("Таблицы между параграфами <p> или внутри тега <article> отсутствуют на странице.")
    
    # else:
    #     print("Микроразметка Open Graph отсутствует на странице.")


    # Возвращаем результат анализа
    analysis_result = {
        "title": title_tag,
        "заголовок содержит ключевое слово": title_contains_keyword,
        "len_title": title_length,
        "число в составе тайтла.": numbers_in_title,
        "Ключевые слова присутствуют": keywords_present,
        "Ключевые слова содержит ключевое слово": keywords_contains_keyword,
        "Количество ключевых слов": keywords_count,
        "Длина ключевых слов": keywords_length,
        "Описание присутствует": description_present,
        "Описание содержит ключевое слово": description_contains_keyword,
        "Длина описания": description_length,
        "Установлен ли язык страницы":lang_attribute,
        "Charset":charset,
        "article_tag":article_tag,
        "H1 присутствует":H1_present,
        "Ключевое слово, найденное в H1":Keyword_found_in_H1,
        "Точное совпадение с названием":Exact_match_with_Title,
        "Присутствует по крайней мере 2 тега H2":At_least_2_H2_tags_present,
        "Ключевое слово, найденно по крайней мере в одном теге H2":Keyword_found_in_at_least_one_H2_tag,
        "TOC присутствует":TOC_present,
        "Все теги H2 должны иметь уникальные идентификаторы":All_H2_tags_should_have_unique_IDs,
    }

    # for item,value in analysis_result.items():
    #     print(item,value)
    return analysis_result


app = FastAPI()

@app.get("/")
async def read_root(request:Request):
    return RedirectResponse(f'{request.url}docs')


@app.get("/analyze/")
async def read_analyze(url: str = Query(...), keyword: str = Query(...)):
    decoded_keyword = unquote(keyword)
    result = analyze_title(url=url, keyword=decoded_keyword)
    return {"result": result}

    

# /analyze/url=https://coffeetehnika.ru/statii/stati-o-kofe/173-arabika-v-kapsulakh-kupite-50-shtuk-po-luchshej-tsene?keyword=Арабика в капсулах


    # print(load_time)
    # print(page_size_kb)
# Пример использования
# url = "https://coffeetehnika.ru/statii/stati-o-kofe/173-arabika-v-kapsulakh-kupite-50-shtuk-po-luchshej-tsene"
# keyword = ""
# analyze_title(url, keyword)