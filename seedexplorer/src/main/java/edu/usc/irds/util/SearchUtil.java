package edu.usc.irds.util;

import edu.usc.irds.fetch.Fetcher;
import edu.usc.irds.model.Query;
import edu.usc.irds.model.QueryResult;
import org.openqa.selenium.*;

import java.util.HashMap;
import java.util.List;

/**
 * Created by ksingh on 2/16/17.
 */
public class SearchUtil {

    private static Integer COUNTER = 0;

    /**
     * Queries Commercial Search Engine (DuckDuckGo) and fetch topN URLs from the result set
     * @param query
     * @param topN
     * @return HashMap of URL - Content
     */
    public static QueryResult queryAndFetch(Query query, Integer topN) {
        System.out.println("Query: " + query.getValue() + "; Region: " + query.getRegion());
        COUNTER++;
        if(COUNTER % 50 == 0) {
            System.out.println(COUNTER + " Queries Executed. Supposed to wait for 10 minutes but let's skip it...");
            /*
            try {
                System.out.println(COUNTER + " Queries Executed. Waiting for 10 minutes...");
                Thread.sleep(600000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            */
        }

        HashMap<String,String> urlContent = new HashMap<>();
        WebDriver driver = null;
        boolean badRequest = false;
        try {
            driver = Fetcher.getSeleniumDriverInstance();
            driver.get("https://api.duckduckgo.com/?q=" + query.getValue() + "&kl=" + query.getRegion());
        }
        catch(Exception e) {
            if(e instanceof TimeoutException) {
                System.out.println("Timeout Exception Raised. Processing whatever loaded so far...");
            }
            else {
                e.printStackTrace();
                badRequest = true;
            }
        }
        finally {
            try {
                if(!badRequest) {
                    int resultSize = 0;
                    List<WebElement> results = driver.findElements(By.className("result__a"));
                    resultSize = results.size();
                    System.out.println("Result Size: " + resultSize);
                    if(results.size() > 0) {
                        while (urlContent.size() < topN && resultSize > 0) {
                            for(WebElement element: results) {
                                String url = element.getAttribute("href");

                                //TODO: Filter URLs if required

                                String content = Fetcher.getPageText(url);
                                if(content == null || content.trim().isEmpty()) {
                                    continue;
                                }
                                urlContent.put(url, content);
                                if(urlContent.size() == topN) {
                                    break;
                                }
                            }
                            if(urlContent.size() < topN) {
                                // Infinite Scroll
                                if (driver instanceof JavascriptExecutor) {
                                    ((JavascriptExecutor) driver)
                                            .executeScript("window.scrollTo(0, document.body.scrollHeight);");
                                }
                                // Filter new results
                                results = driver.findElements(By.className("result__a"));
                                results = results.subList(resultSize, results.size());
                                resultSize = results.size();
                                System.out.println("Moved to Next Page. Result Size: " + resultSize);
                            }
                        }
                    }
                }
            }
            catch(Exception e) {
                e.printStackTrace();
            }
            finally {
                if(driver != null) {
                    try {
                        driver.close();
                        driver.quit();
                    }
                    catch(Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        }

        System.out.println("Search Completed");

        QueryResult queryResult = new QueryResult(query, urlContent);
        return queryResult;
    }

    /**
     * Queries Commercial Search Engine (DuckDuckGo) and fetch top 10 URLs from the result set
     * @param query
     * @return HashMap of URL - Content
     */
    public static QueryResult queryAndFetch(Query query) {
        return queryAndFetch(query, 10);
    }


    public static void main(String[] args) {
        Query query = new Query("nsidc");
        for(String url: queryAndFetch(query, 30).getUrlContent().keySet()) {
            System.out.println(url);
        }
    }
}
