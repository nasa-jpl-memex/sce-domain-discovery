package edu.usc.irds.fetch;

import de.l3s.boilerpipe.BoilerpipeProcessingException;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import edu.usc.irds.model.FetchedData;
import edu.usc.irds.util.Constants;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxBinary;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.firefox.internal.ProfilesIni;

import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

/**
 * Created by ksingh on 2/16/17.
 */
public class Fetcher {

    private static FirefoxProfile ffxProfile;
    private static FirefoxBinary ffxBinary;


    static {
        ProfilesIni allProfiles = new ProfilesIni();
        ffxProfile = allProfiles.getProfile("default");
        ffxProfile.setPreference(FirefoxProfile.ALLOWED_HOSTS_PREFERENCE, Constants.FFX_HOST);
        ffxBinary = new FirefoxBinary(new File(Constants.FFX_BIN_PATH));
        ffxBinary.setTimeout(TimeUnit.SECONDS.toMillis(Constants.FFX_TIMEOUT_SECS));
    }


    public static WebDriver getSeleniumDriverInstance() {
        WebDriver driver = new FirefoxDriver(ffxBinary, ffxProfile);
        driver.manage().timeouts().pageLoadTimeout(Constants.PAGE_TIMEOUT_SECS, TimeUnit.SECONDS);
        return driver;
    }


    public static void closeSeleniumDriverInstance(WebDriver driver) {
        if(driver != null) {
            try {
                driver.close();
                driver.quit();
            }
            catch(Exception se2) {
                System.out.println("Exception on closing the browser!!");
                se2.printStackTrace();
            }
        }
    }


    /**
     * Fetch a URL using Jsoup
     * @param url
     * @return
     * @throws Exception
     */
    public static FetchedData jsoup(String url) throws Exception {
        Connection.Response response;
        Document htmlContent;
        FetchedData data = new FetchedData();

        response = Jsoup.connect(url).userAgent(Constants.JSOUP_USER_AGENT).followRedirects(true).execute();
        htmlContent = response.parse();
        data.setHtml(htmlContent.html());
        if(Constants.IS_BOILERPIPE)
            data.setText(ArticleExtractor.INSTANCE.getText(htmlContent.html()));
        else
            data.setText(htmlContent.getElementsByTag("body").text());
        return data;
    }


    /**
     * Fetch a URL using Selenium-Firefox
     * @param url
     * @return FetchedData
     */
    public static FetchedData selenium(String url) {
        WebDriver driver = getSeleniumDriverInstance();
        boolean badRequest = false;
        FetchedData data = new FetchedData();
        try {
            driver.get(url);
        }
        catch(Exception se) {
            if(se instanceof TimeoutException) {
                System.out.println("Timeout Exception Raised. Processing whatever loaded so far...");
            }
            else {
                se.printStackTrace();
                System.out.println("Bad Request. Ignoring Content...");
                badRequest = true;
            }
        }
        finally {
            try {
                if(!badRequest) {
                    data.setHtml(driver.getPageSource());
                    if(Constants.IS_BOILERPIPE)
                        data.setText(ArticleExtractor.INSTANCE.getText(driver.getPageSource()));
                    else
                        data.setText(driver.findElement(By.tagName("body")).getText());
                }
            }
            catch(Exception se1) {
                se1.printStackTrace();
            }
            finally {
                closeSeleniumDriverInstance(driver);
            }
        }
        return data;
    }


    /**
     * Fetch a URL using jsoup. If it fails then use selenium-firefox
     * @param url
     * @return FetchedData
     */
    public static FetchedData fetch(String url) {
        //System.out.println("Fetching: " + url);

        FetchedData data;
        try {
            // Fetch page using JSOUP
            data = jsoup(url);
        }
        catch(Exception e) {
            System.out.println("Exception Raised while fetching content using JSOUP. Trying Selenium now...");

            // Fetch page using Selenium
            data = selenium(url);
        }
        return data;
    }

    /**
     * Retrieves page text
     * @param url
     * @return
     * @throws UnsupportedEncodingException
     */
    public static String getPageText(String url) throws UnsupportedEncodingException {
        FetchedData data = fetch(url);
        return new String(data.getText().getBytes("UTF-8"));
    }

    /**
     * Gives back a map of <Url, Text> for a given list of urls provides
     * @param urls
     * @return
     * @throws InterruptedException
     * @throws IOException
     */
    public static LinkedHashMap<String,String> getAllPageTexts(LinkedHashSet<String> urls) throws InterruptedException, IOException{
        LinkedHashMap<String,String> text=new LinkedHashMap<String,String>();

        for (String url: urls){
            try{
                text.put(url, getPageText(url));
            }
            catch(Exception e){
                System.out.println("Problem fetching: " + url);
                e.printStackTrace();
            }
        }
        return text;
    }

    /**
     * Retrieves page Html
     * @param url
     * @return
     * @throws UnsupportedEncodingException
     */
    public static String getPageHtml(String url) throws UnsupportedEncodingException {
        FetchedData data = fetch(url);
        return new String(data.getHtml().getBytes("UTF-8"));
    }

}
