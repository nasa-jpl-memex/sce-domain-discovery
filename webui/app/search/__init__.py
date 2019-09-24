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


logging.basicConfig(level=logging.DEBUG)
url_details = []
url_text = []
db = None
models = None
aurl = os.getenv('ARANGO_URL', 'https://single-server-int:8529')
conn = Connection(aurl, 'root', '',verify=False)
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

    start_pos = top_n * (page-1)
    end_pos = start_pos+top_n

    output = ""
    try:
        app.logger.info('Processing get url request '+ query)
        #driver = Fetcher.get_selenium_driver()
        #driver.get('https://duckduckgo.com/?q=' + query + '&kl=wt-wt&ks=l&k1=-1&kp=-2&ka=a&kaq=-1&k18=-1&kax=-1&kaj=u&kac=-1&kn=1&kt=a&kao=-1&kap=-1&kak=-1&kk=-1&ko=s&kv=-1&kav=1&t=hk&ia=news')
        output = requests.get("http://sce-splash:8050/render.html?url=https%3A%2F%2Fduckduckgo.com%2F%3Fq%3Darctic%20policy%20national%26kl%3Dwt-wt%26ks%3Dl%26k1%3D-1%26kp%3D-2%26ka%3Da%26kaq%3D-1%26k18%3D-1%26kax%3D-1%26kaj%3Du%26kac%3D-1%26kn%3D1%26kt%3Da%26kao%3D-1%26kap%3D-1%26kak%3D-1%26kk%3D-1%26ko%3Ds%26kv%3D-1%26kav%3D1%26t%3Dhk%26ia%3Dnews&wait=5").content
    except:
        app.logger.info('An error occurred while searching query: ' + query)
        app.logger.info(traceback.format_exc())
        #Fetcher.close_selenium_driver(driver)
        #Fetcher.search_driver = None
        bad_request = True

    finally:
        try:
            if not bad_request:
                #results = driver.find_elements_by_class_name('result__a')
                soup = BeautifulSoup(output, 'html.parser')
                results = soup.findAll("a", {"class": "result__a"})
                result_size = len(results)
                app.logger.info('Results Found ' + str(result_size))
                prev_length = 0
                t = 0
                # while result_size < end_pos:
                #     driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                #     results = driver.find_elements_by_class_name('result__a')
                #     result_size = len(results)
                #     if result_size == prev_length:
                #         t=t+1
                #         if t == 4:
                #             break;
                #     else:
                #         prev_length = result_size
                #
                #     print('Moved to Next Page. Result Size: ' + str(result_size))
                return results[start_pos:end_pos]
        except Exception as e:
            app.logger.info(e)
            print('An error occurred while searching query: '+ query + ' and fetching results')

def query_and_fetch(query, model, top_n=12, page=1):
    """Query Duck Duck Go (DDG) for top n results"""
    global url_details, url_text
    print('Query: ' + query + '; Top N: ' + str(top_n))
    url_details = []
    url_text = []
    url_image = []
    driver = None
    bad_request = False
    try:
        results = get_url_window(query,top_n, page)

    except:
        app.logger.info('An error occurred while searching query: ' + query)
        app.logger.info(traceback.format_exc())
        #Fetcher.close_selenium_driver(driver)
        #Fetcher.search_driver = None
        bad_request = True

    finally:
        try:
            if not bad_request:
                result_size = len(results)
                print('Result Size: ' + str(result_size))
                app.logger.info('Results Found ' + str(result_size))
                urls = []
                for element in results:
                    new_url = element['href']
                    app.logger.info('Adding URL ' + new_url)
                    urls.append(new_url)

                while result_size > 0 and len(url_details) < top_n:
                    fetched_result = Fetcher.fetch_multiple(urls, top_n)
                    app.logger.info("Looping: "+str(len(fetched_result)) +"times")
                    for fetched_data in fetched_result:
                        try:
                            if not fetched_data[1] or len(fetched_data[1].strip()) == 0:
                                continue
                            details = dict()
                            details['url'] = fetched_data[0]
                            details['html'] = fetched_data[1]
                            details['title'] = fetched_data[2]
                            details['label'] = predict(model, fetched_data[3])
                            print("Fetching image for " +fetched_data[0])
                            app.logger.info('Fetching image for ' + fetched_data[0])
                            try:
                                app.logger.info("http://sce-splash:8050/render.png?url="+fetched_data[0]+"&width=320&height=240")
                                details['image'] = base64.b64encode(requests.get("http://sce-splash:8050/render.png?url="+fetched_data[0]+"&wait=5&width=320&height=240").content)
                            except Exception:
                                continue
                            url_details.append(details)
                            url_text.append(fetched_data[3])
                            if len(url_details) == top_n:
                                break
                        except:
                            print("catching timeout exception")
                            continue
        except Exception as e:
            app.logger.info(e)
            app.logger.info('An error occurred while searching query: '+ query + ' and fetching results')
        finally:
           if driver is not None:
               Fetcher.close_selenium_driver(driver)

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
    print('Query: ' + q + '; Top N: ' + str(top_n))

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
