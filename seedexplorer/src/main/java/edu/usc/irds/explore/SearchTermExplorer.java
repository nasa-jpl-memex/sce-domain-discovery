package edu.usc.irds.explore;

import com.google.common.base.Charsets;
import com.google.common.io.Resources;
import edu.usc.irds.model.Query;
import edu.usc.irds.model.QueryResult;
import edu.usc.irds.parse.LangParser;
import edu.usc.irds.util.CosineUtil;
import edu.usc.irds.util.FileUtil;
import edu.usc.irds.util.SearchUtil;
import org.apache.commons.io.IOUtils;

import java.io.*;
import java.util.*;

/**
 * Created by ksingh on 2/20/17.
 */
public class SearchTermExplorer {

    private String keywords;
    private Set<String> searchTerms;

    public SearchTermExplorer(String keywordsPath, String searchTermsPath) {
        try {
            keywords = Resources.toString(Resources.getResource(keywordsPath), Charsets.UTF_8);
            searchTerms = FileUtil.readLinesInSet(SearchTermExplorer.class.getClassLoader().getResourceAsStream(searchTermsPath));
        } catch (IOException e) {
            e.printStackTrace();
            System.out.println("Exception raised while reading data.");
        }
    }

    public List<Map.Entry<String, Double>> sortByValue(HashMap<String, Double> map) {
        List<Map.Entry<String, Double>> list = new ArrayList<>(map.entrySet());
        Collections.sort(list, new Comparator<Map.Entry<String, Double>>() {
            @Override
            public int compare(Map.Entry<String, Double> o1, Map.Entry<String, Double> o2) {
                return (o2.getValue()).compareTo(o1.getValue());
            }
        });
        return list;
    }

    public void explore() throws IOException {
        // Build Domain Relevancy Model
        List<String> relevantContent = new ArrayList<>();
        relevantContent.add(keywords);
        CosineUtil.parseFile(relevantContent);

        // Constructing and Executing Queries
        List<QueryResult> results = new ArrayList<>();
        for (String term: searchTerms) {
            Query query = new Query(term);
            QueryResult result = SearchUtil.queryAndFetch(query, 25);
            results.add(result);
        }

        // Scoring URLs
        HashMap<String, Double> urlScore = new HashMap<>();
        Double score = 0.0;
        for (QueryResult result: results) {
            HashMap<String, Double> urlScoresResult = new HashMap<>();
            for (Map.Entry<String, String> entry: result.getUrlContent().entrySet()) {
                score = CosineUtil.getCosineSimilarity(
                            CosineUtil.tfIdfCalculator(
                                CosineUtil.tokenizeintoBOW(CosineUtil.STOP_WORDS, entry.getValue(), LangParser.posTagger)), -1);
                if(score.isNaN())
                    continue;
                urlScore.put(entry.getKey(), score);
                urlScoresResult.put(entry.getKey(), score);
            }
            result.setUrlScore(urlScoresResult);
        }


        // Output to File
        File out = new File("searchTermExplorer.out." + new Date().getTime());
        BufferedWriter bw = null;

        // Print Rank Sorted URLs
        List<Map.Entry<String, Double>> sortedEntries = sortByValue(urlScore);
        for (Map.Entry<String, Double> entry: sortedEntries) {
            try {
                bw = new BufferedWriter(new FileWriter(out, true));
                String row = "\"" + entry.getValue() + "\",\"" + entry.getKey() + "\"";
                bw.write(row);
            } catch (IOException e) {
                e.printStackTrace();
                System.out.println("Exception Raised while writing to the file");
            } finally {
                IOUtils.closeQuietly(bw);
            }
            System.out.println("\"" + entry.getValue() + "\",\"" + entry.getKey() + "\"");
        }
    }


    public static void main(String[] args) throws IOException {
        SearchTermExplorer explorer = new SearchTermExplorer("data/keywords.txt",
                "data/search_terms.txt");
        explorer.explore();
    }

}
