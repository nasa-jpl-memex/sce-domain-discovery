from app.search.fetcher import Fetcher
from app.classifier import predict
import flask

url_details = []
url_text = []


def query_and_fetch(query, top_n=12):
    """Query Duck Duck Go (DDG) for top n results"""
    global url_details, url_text
    print('Query: ' + query + '; Top N: ' + str(top_n))
    url_details = []
    url_text = []
    driver = None
    bad_request = False
    try:
        driver = Fetcher.get_selenium_driver()
        driver.get('https://api.duckduckgo.com/?q=' + query + '&kl=wt-wt')
    except:
        print('An error occurred while searching query: ' + query)
        bad_request = True
    finally:
        try:
            if not bad_request:
                results = driver.find_elements_by_class_name('result__a')
                result_size = len(results)
                print('Result Size: ' + str(result_size))
                while result_size > 0 and len(url_details) < top_n:
                    for element in results:
                        new_url = element.get_attribute('href')
                        # TODO: Filter URLs if required
                        print(new_url)
                        fetched_data = Fetcher.fetch(new_url)
                        if not fetched_data[0] or len(fetched_data[0].strip()) == 0:
                            continue
                        #print('Adding content for URL: ' + new_url)
                        details = dict()
                        details['url'] = new_url
                        details['html'] = fetched_data[0]
                        details['title'] = fetched_data[1]
                        details['label'] = predict(fetched_data[2])
                        url_details.append(details)
                        url_text.append(fetched_data[2])
                        if len(url_details) == top_n:
                            break

                    # Infinite Scroll
                    if len(url_details) < top_n:
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        results = driver.find_elements_by_class_name('result__a')
                        results = results[result_size:]
                        result_size = len(results)
                        print('Moved to Next Page. Result Size: ' + str(result_size))
        except:
            print('An error occurred while searching query: '+ query + ' and fetching results')
        #finally:
        #    if driver is not None:
        #        Fetcher.close_selenium_driver(driver)
    setattr(flask.current_app, 'url_text', url_text)
    print('Search Completed')
    return url_details


def query(q, top_n=12):
    """Query Duck Duck Go (DDG) for top n results"""
    print('Query: ' + q + '; Top N: ' + str(top_n))

    driver = None
    bad_request = False
    urls = set()
    try:
        driver = Fetcher.get_selenium_driver()
        driver.get('https://api.duckduckgo.com/?q=' + q + '&kl=wt-wt')
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


#output = query_and_fetch('tesla')
#for url in output:
#    print(url)
