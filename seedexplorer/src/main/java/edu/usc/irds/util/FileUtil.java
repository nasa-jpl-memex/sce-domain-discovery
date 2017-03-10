package edu.usc.irds.util;

import org.apache.commons.io.IOUtils;

import java.io.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Created by ksingh on 2/16/17.
 */
public class FileUtil {

    /**
     * Read all lines of a file into an ArrayList
     * @param filename
     * @return List<String> with each line as a separate item in the list
     * @throws IOException
     */
    public static List<String> readLinesInList(String filename) throws IOException {
        List<String> lines = new ArrayList<String>();
        File file = null;
        FileReader reader = null;
        BufferedReader bufferedReader = null;
        String line = null;
        try {
            file = new File(filename);
            reader = new FileReader(file);
            bufferedReader = new BufferedReader(reader);

            while((line = bufferedReader.readLine()) != null)
                lines.add(line);
        }
        finally {
            if(bufferedReader != null)
                bufferedReader.close();
            if(reader != null)
                reader.close();
        }
        return lines;
    }

    /**
     * Read all lines of a file into a HashSet
     * @param filename
     * @return Set<String> with each line as a separate item in the set and de-duplicated
     * @throws IOException
     */
    public static Set<String> readLinesInSet(String filename) throws IOException {
        return new HashSet<>(readLinesInList(filename));
    }


    public static List<String> readLinesInList(InputStream stream) throws IOException {
        List<String> lines = new ArrayList<String>();
        BufferedReader bufferedReader = null;
        String line = null;
        try {
            bufferedReader = new BufferedReader(new InputStreamReader(stream));

            while((line = bufferedReader.readLine()) != null)
                lines.add(line);
        }
        finally {
            IOUtils.closeQuietly(bufferedReader);
        }
        return lines;
    }

    public static Set<String> readLinesInSet(InputStream stream) throws IOException {
        return new HashSet<>(readLinesInList(stream));
    }

}
