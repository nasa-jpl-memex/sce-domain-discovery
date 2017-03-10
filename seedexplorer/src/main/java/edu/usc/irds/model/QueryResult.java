package edu.usc.irds.model;

import java.util.HashMap;

/**
 * Created by ksingh on 2/19/17.
 */
public class QueryResult {

    private Query query;
    private Double score;
    private HashMap<String, Double> urlScore;
    private HashMap<String, String> urlContent;

    public QueryResult(Query query, HashMap<String, String> urlContent) {
        this.query = query;
        this.urlContent = urlContent;
    }

    public Query getQuery() { return query; }

    public void setQuery(Query query) {
        this.query = query;
    }

    public Double getScore() {
        return score;
    }

    public void setScore(Double score) {
        this.score = score;
    }

    public HashMap<String, Double> getUrlScore() {
        return urlScore;
    }

    public void setUrlScore(HashMap<String, Double> urlScore) {
        this.urlScore = urlScore;
    }

    public HashMap<String, String> getUrlContent() {
        return urlContent;
    }

    public void setUrlContent(HashMap<String, String> urlContent) {
        this.urlContent = urlContent;
    }
}
