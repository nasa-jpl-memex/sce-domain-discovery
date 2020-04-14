import base64

from pyArango.theExceptions import DocumentNotFoundError
from selenium.common.exceptions import TimeoutException

from fetcher import Fetcher
from app.classifier import predict
import traceback
from pyArango.connection import *
import os
from flask import current_app as app
import logging
from bs4 import BeautifulSoup
import requests
import uuid
import urllib

logging.basicConfig(level=logging.DEBUG)
url_details = []
url_text = []
db = None
models = None
aurl = os.getenv('ARANGO_URL', 'https://single-server-int:8529')
conn = Connection(aurl, 'root', '', verify=False)
if not conn.hasDatabase("sce"):
    db = conn.createDatabase("sce")
else:
    db = conn["sce"]

if not db.hasCollection('models'):
    models = db.createCollection('Collection', name='models')
else:
    models = db.collections['models']


def get_url_window(query, top_n, page):
    bad_request = False

    start_pos = top_n * (page - 1)
    end_pos = start_pos + top_n

    output = ""
    try:
        app.logger.info('Processing get url request ' + query)
        query = urllib.quote(query)
        o = "http://sce-splash:8050/render.html?url=https%3A%2F%2Fduckduckgo.com%2F%3Fq%3D" + query + "%26kl%3Dwt-wt%26ks%3Dl%26k1%3D-1%26kp%3D-2%26ka%3Da%26kaq%3D-1%26k18%3D-1%26kax%3D-1%26kaj%3Du%26kac%3D-1%26kn%3D1%26kt%3Da%26kao%3D-1%26kap%3D-1%26kak%3D-1%26kk%3D-1%26ko%3Ds%26kv%3D-1%26kav%3D1%26t%3Dhk%26ia%3Dnews&wait=5"
        #o = "http://localhost:8050/render.html?url=https%3A%2F%2Fduckduckgo.com%2F%3Fq%3D" + query + "%26kl%3Dwt-wt%26ks%3Dl%26k1%3D-1%26kp%3D-2%26ka%3Da%26kaq%3D-1%26k18%3D-1%26kax%3D-1%26kaj%3Du%26kac%3D-1%26kn%3D1%26kt%3Da%26kao%3D-1%26kap%3D-1%26kak%3D-1%26kk%3D-1%26ko%3Ds%26kv%3D-1%26kav%3D1%26t%3Dhk%26ia%3Dnews&wait=5"
        output = requests.get(o).content
    except:
        app.logger.info('An error occurred while searching query: ' + query)
        app.logger.info(traceback.format_exc())
        bad_request = True

    finally:
        try:
            if not bad_request:
                soup = BeautifulSoup(output, 'html.parser')
                results = soup.findAll("a", {"class": "result__a"})
                result_size = len(results)
                app.logger.info('Results Found ' + str(result_size))
                t = 0
                return results[start_pos:end_pos]
        except Exception as e:
            app.logger.info(e)
            print('An error occurred while searching query: ' + query + ' and fetching results')


def query_and_fetch(query, model, top_n=12, page=1):
    """Query Duck Duck Go (DDG) for top n results"""
    global url_details, url_text
    app.logger.debug('Query456: ' + query + '; Top N: ' + str(top_n))
    url_details = []
    url_text = []
    bad_request = False
    try:
        results = get_url_window(query, top_n, page)

    except:
        app.logger.info('An error occurred while searching query: ' + query)
        app.logger.info(traceback.format_exc())
        bad_request = True

    if not bad_request:
        urls = []
        for element in results:
            new_url = element['href']
            urls.append(new_url)
        fetched_result = Fetcher.fetch_multiple(urls, None)
        for fetched_data in fetched_result:
            if fetched_data is not None:
                if len(url_details) == 12:
                    break
                else:
                    try:
                        if not fetched_data[1] or len(fetched_data[1].strip()) == 0:
                            app.logger.info("Continuing")
                            continue

                        app.logger.info("Extracting URL: " + fetched_data[0])
                        details = dict()
                        details['url'] = fetched_data[0]
                        details['html'] = fetched_data[1]
                        details['title'] = fetched_data[2]
                        details['label'] = predict(model, fetched_data[3])
                        try:
                            print("http://localhost:8050/render.png?url=" + fetched_data[0] + "&wait=5&width=320&height=240")
                            imag = requests.get("http://localhost:8050/render.png?url=" + fetched_data[0] + "&wait=5&width=320&height=240")

                            #imag = requests.get("http://sce-splash:8050/render.png?url=" + fetched_data[0] + "&wait=5&width=320&height=240")

                            if imag.status_code == 200:
                                u = str(uuid.uuid4())
                                with open("/images/" + u + ".png", 'wb') as f:
                                    f.write(imag.content)
                                details['image'] = "/images/" + u + ".png"

                                with open(details['image'], "rb") as image_file:
                                    encoded_string = base64.b64encode(image_file.read())
                                    details['image'] = encoded_string.decode()

                        except Exception as e:
                            app.logger.info(e)
                            continue
                        url_details.append(details)
                        url_text.append(fetched_data[3])
                    except Exception as e:
                        print("catching timeout exception")
                        app.logger.debug("catching exception down here! "+ str(e))
                        continue

    try:
        model = models[model]
        model['url_text'] = url_text
        model['url_details'] = url_details
        model.save()
    except DocumentNotFoundError as error:
        app.logger.info(error)
        raise

    print('Search Completed')
    app.logger.info('Search Completed')

    return url_details


def query(q, top_n=12):
    """Query Duck Duck Go (DDG) for top n results"""
    print('Query123: ' + q + '; Top N: ' + str(top_n))

    driver = None
    bad_request = False
    urls = set()
    try:
        driver = Fetcher.get_selenium_driver()
        driver.get('https://duckduckgo.com/html/?q=' + q + '&kl=wt-wt')
    except:
        print('An error occurred while searching query: ' + q)
        bad_request = True
    finally:
        try:
            if not bad_request:
                results = driver.find_elements_by_class_name('result__a')
                result_size = len(results)
                print('Result Size: ' + str(result_size))
                while result_size > 0 and len(urls) < top_n:
                    for element in results:
                        new_url = element.get_attribute('href')
                        # TODO: Filter URLs if required
                        urls.add(new_url)
                        if len(urls) == top_n:
                            break

                    # Infinite Scroll
                    if len(urls) < top_n:
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        results = driver.find_elements_by_class_name('result__a')
                        results = results[result_size:]
                        result_size = len(results)
                        print('Moved to Next Page. Result Size: ' + str(result_size))
        except:
            print('An error occurred while searching query: ' + q + ' and fetching results')
        finally:
            if driver:
                Fetcher.close_selenium_driver(driver)
    print('Search Completed')
    return urls
