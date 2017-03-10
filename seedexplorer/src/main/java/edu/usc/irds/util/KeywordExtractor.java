package edu.usc.irds.util;

import edu.usc.irds.fetch.Fetcher;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.math.NumberUtils;
import org.apache.pdfbox.tools.PDFText2HTML;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.Parser;
import org.apache.tika.parser.html.HtmlParser;
import org.apache.tika.parser.pdf.PDFParser;
import org.apache.tika.sax.BodyContentHandler;
import org.apache.tika.sax.ToHTMLContentHandler;
import org.apache.tika.sax.XHTMLContentHandler;
import org.apache.xml.serializer.ToHTMLSAXHandler;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.xml.sax.ContentHandler;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;
import java.io.*;
import java.util.HashSet;
import java.util.Set;

/**
 * Created by ksingh on 2/24/17.
 */
public class KeywordExtractor {

    private static KeywordExtractor extractor;
    private XPath xpath;

    private KeywordExtractor() {
        xpath = XPathFactory.newInstance().newXPath();
    }

    public static KeywordExtractor getInstance() {
        if(extractor == null) {
            extractor = new KeywordExtractor();
        }
        return extractor;
    }

    public String byXPath(String html, String expression) throws XPathExpressionException {
        Document doc = Jsoup.parse(html);
        // /xpath.compile(expression);
        //String result = xpath.evaluate(html, XPathConstants.STRING);
        //System.out.println(result);
        return null;
    }

    public String byCss(String html, String expression) throws Exception {
        Document doc = Jsoup.parse(html);
        Elements elements = doc.select(expression);
        return elements.html();
    }

    public static String getText(String html) throws Exception {
        ContentHandler handler = new BodyContentHandler();
        Metadata metadata = new Metadata();
        new HtmlParser().parse(new ByteArrayInputStream(html.getBytes()), handler, metadata, new ParseContext());
        return handler.toString();
    }

    public static String keywords(String text) {
        return text.replaceAll("\\n"," ").replaceAll("[^a-zA-Z0-9 ]+"," ");
    }

    public static String unique(String text) {
        String[] words = text.split(" ");
        Set<String> uniqueWords = new HashSet<>();
        for (String word : words) {
            if(word != null) {
                word = word.trim();
                if (word.length() > 1) {
                    uniqueWords.add(word.toLowerCase());
                }
            }
        }
        return StringUtils.join(uniqueWords, " ");
    }

    public Elements fromPdf(String path) throws Exception {
        Parser parser = new PDFParser();
        OutputStream outputStream = new ByteArrayOutputStream();
        ContentHandler htmlContentHandler = new ToHTMLContentHandler(outputStream, "UTF-8");
        Metadata metadata = new Metadata();
        XHTMLContentHandler xhtmlContentHandler = new XHTMLContentHandler(htmlContentHandler, metadata);
        ParseContext context = new ParseContext();
        InputStream inputStream = new FileInputStream(path);
        String html = "";

        try {
            parser.parse(inputStream, xhtmlContentHandler, metadata, context);
            html = outputStream.toString();
        } finally {
            IOUtils.closeQuietly(inputStream);
            IOUtils.closeQuietly(outputStream);
        }

        Document doc = Jsoup.parse(html);
        Elements elements =  doc.select(".page");
        System.out.println("Total Pages: " + elements.size());
        return elements;
    }

    public Elements fromPdf(String path, Integer startPage, Integer endPage) throws Exception {
        if(startPage > endPage)
            return new Elements();
        Elements elements =  fromPdf(path);
        Elements filteredElements = new Elements();
        int currentPage = 0;
        for(Element element: elements) {
            currentPage++;
            if(currentPage >= startPage && currentPage <= endPage) {
                filteredElements.add(element);
            }
        }
        return filteredElements;
    }

    public static void main(String[] args) throws Exception {
        //String url = "https://pubs.usgs.gov/of/2004/1216/text.html";
        //String url = "http://nsidc.org/cryosphere/glossary/";
        String url = "http://www.avalanches.org/eaws/en/includes/glossary/glossary_en_all.html";
        //String expression = ".field-items h2";
        String expression = "#box h3";
        //for(int i = 65; i < 91; i++) {
        //    char c = (char)i;
        //    System.out.println(KeywordExtractor.getInstance().byCss(Fetcher.getPageHtml(url), expression));
        //}

        //String html = KeywordExtractor.getInstance().byCss(Fetcher.getPageHtml(url), expression);
        //System.out.println(unique(keywords(getText(html))));

        /*
        Elements elements = KeywordExtractor.getInstance().fromPdf("/Users/ksingh/Downloads/192525E.pdf", 30, 30);
        for(Element element: elements) {
            System.out.println(element);
        }
        */

        /* Extraction of Sea Ice Terms
        Elements elements = KeywordExtractor.getInstance().fromPdf("/Users/ksingh/Downloads/Sea_Ice_Nomenclature_March_2014.pdf", 6, 48);
        StringBuilder sb = new StringBuilder();
        for(Element element: elements) {
            Elements paragraphs = element.select("p");
            for(Element paragraph: paragraphs) {
                if(NumberUtils.isNumber(paragraph.text().trim().split(" ")[0])) {
                    sb.append(StringUtils.substringBetween(paragraph.text(), " ", ":"))
                    .append(" ");
                }
            }
        }
        System.out.println(unique(sb.toString()));
        */
    }
}
