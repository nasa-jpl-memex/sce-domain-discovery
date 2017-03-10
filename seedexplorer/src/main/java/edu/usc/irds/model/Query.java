package edu.usc.irds.model;

/**
 * Created by ksingh on 2/19/17.
 */
public class Query {

    private String value;
    private String region;

    // DuckDuckGo format for an empty region
    public static final String NO_REGION = "wt-wt";

    public Query(String value) {
        this.value = value;
        region = NO_REGION;
    }

    public Query(String value, String region) {
        this.value = value;
        this.region = region;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getRegion() {
        return region;
    }

    public void setRegion(String region) {
        this.region = region;
    }
}
