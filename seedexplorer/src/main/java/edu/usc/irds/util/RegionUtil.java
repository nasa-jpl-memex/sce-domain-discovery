package edu.usc.irds.util;

import org.apache.commons.io.IOUtils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/**
 * Created by ksingh on 2/19/17.
 */
public class RegionUtil {

    private static HashMap<String, List<String>> cityRegion = new HashMap<>();
    private static HashMap<String, List<String>> stateRegion = new HashMap<>();
    private static HashMap<String, List<String>> regionCode = new HashMap<>();

    static {
        loadData();
    }

    private static void loadData() {
        loadCsv("city_region.csv", cityRegion);
        loadCsv("state_region.csv", stateRegion);
        loadCsv("region.csv", regionCode);
    }

    private static void loadCsv(String filename, HashMap<String, List<String>> object) {
        String line;
        String delimiter = ",";
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(RegionUtil.class.getClassLoader().getResourceAsStream(filename)));
            while ((line = br.readLine()) != null) {
                String[] mapping = line.split(delimiter);
                String key = mapping[0].toLowerCase();
                String value = mapping[1].toLowerCase();
                if (object.containsKey(key)) {
                    object.get(key).add(value);
                } else {
                    List<String> values = new ArrayList<>();
                    values.add(value);
                    object.put(key, values);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Exception raised while loading csv: "+ filename);
        } finally {
            IOUtils.closeQuietly(br);
        }
    }

    public static List<String> getRegion(String location) {
        String formatLocation = location.toLowerCase();
        List<String> regions = new ArrayList<>();
        if (cityRegion.containsKey(formatLocation)) {
            for (String region: cityRegion.get(formatLocation)) {
                for (String code: regionCode.get(region)) {
                    regions.add(code);
                }
            }
        } else if (stateRegion.containsKey(formatLocation)) {
            for (String region: stateRegion.get(formatLocation)) {
                for (String code: regionCode.get(region)) {
                    regions.add(code);
                }
            }
        }
        return regions;
    }


    public static void main (String[] args) {
        List<String> regions = getRegion("los angeles");
        if (!regions.isEmpty()) {
            for (String region: regions) {
                System.out.println(region);
            }
        }
    }
}
