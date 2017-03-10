package edu.usc.irds.util;


import java.io.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeMap;
import java.util.regex.Pattern;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.usc.irds.parse.LangParser;


/**
 * A class to calculate the Cosine Similarity between documents/texts
 * It allows for you to create a knowledge base which you can use for
 * 1. averages similarity calculation
 * 2. update/manipulate the idf calculation in a decoupled way
 * @author asitangmishra
 * @modified_by karanjeetsingh
 *
 */
public class CosineUtil {

    /**
     * A Map to store word and their count in the whole corpus: used in the calculation of idf
     */
    public static HashMap<String, Double> allTermCounts = new HashMap<String, Double>();

    /**
     * A list of vectors that can constitute of your kb-vectors
     */
    public static HashSet<HashMap<String, Double>> vectors = new HashSet<HashMap<String, Double>>();

    /**
     * Total number of docs we ingested to create the idf-kb: "allTermCounts" and "totaldocs"
     */
    public static double totaldocs = 0.0;

    public static final String STOP_WORDS = "stopwords.txt";




    /**
     * Tokenizes the text using core nlp in the following piepline: see commnets inline
     * @param stopwordlistpath
     * @param text
     * @param tagger
     * @return
     * @throws IOException
     */
    public static String[] tokenizeintoBOW(String stopwordlistpath,String text,MaxentTagger tagger) throws IOException{



        ArrayList<String> bow=new ArrayList<String>();


        //remove stop words
        HashSet<String> stopdict=new HashSet<String>();
        //FileReader fileReader = new FileReader("/Users/asitangm/Desktop/JPL/files/internet-stopwords");
        String line="";
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(CosineUtil.class.getClassLoader().getResourceAsStream(stopwordlistpath)));
        //BufferedReader bufferedReader = new BufferedReader(fileReader);

        while ((line = bufferedReader.readLine()) != null) {
            stopdict.add(line);
        }

        bufferedReader.close();


        //remove the non-relevant pos tags
        HashSet<String> stopdictpos=new HashSet<String>();


        stopdictpos.add("CC");
        stopdictpos.add("CD");
        stopdictpos.add("LS");
        stopdictpos.add("TO");
        stopdictpos.add("SYM");
        stopdictpos.add("PRP");
        stopdictpos.add("PRP$");
        stopdictpos.add("WDT");
        stopdictpos.add("WP");
        stopdictpos.add("WP$");
        stopdictpos.add("EX");
        stopdictpos.add("UH");


        //remove any words that have any spl character in them
        Pattern p = Pattern.compile("[^a-z0-9 ]", Pattern.CASE_INSENSITIVE);

        //tokenize and store the lowercase
        DocumentPreprocessor tokenizer = new DocumentPreprocessor(
                new StringReader(text));

        for (List<HasWord> sentence : tokenizer) {
            List<TaggedWord> tagged = tagger.tagSentence(sentence);

            for(TaggedWord tword:tagged){

                if(!stopdict.contains(tword.word().toLowerCase())&&!stopdictpos.contains(tword.tag().toString())&&!p.matcher(tword.word().toString()).find()){
                    bow.add(tword.word().toLowerCase());

                }
            }
        }

        return  bow.toArray(new String[bow.size()]);

    }


    /**
     * A simple utility function that updates the value of an entry in a Map by some amount
     * @param word
     * @param map
     * @param by
     */
    public static void updateMap(String word, HashMap<String, Double> map,
                                 double by) {

        if (map.containsKey(word)) {
            map.put(word, map.get(word) + by);
        } else {
            map.put(word, by);
        }
    }

    /**
     * Calculates cosine Similarity between two vectors
     * @param vector1
     * @param vector2
     * @return
     */
    public static double cosineSimilarity(HashMap<String, Double> vector1,
                                          HashMap<String, Double> vector2) {
        double dotProduct = 0.0;
        double magnitude1 = 0.0;
        double magnitude2 = 0.0;
        double cosineSimilarity = 0.0;

        for (String term : vector1.keySet())
        {
            if (vector2.containsKey(term)) {
                dotProduct += vector1.get(term) * vector2.get(term); // a.b
            }
        }

        for(String term :vector1.keySet()){
            magnitude1 += Math.pow(vector1.get(term), 2); // (a^2)
        }

        for(String term :vector2.keySet()){
            magnitude2 += Math.pow(vector2.get(term), 2); // (a^2)
        }

        magnitude1 = Math.sqrt(magnitude1);// sqrt(a^2)
        magnitude2 = Math.sqrt(magnitude2);// sqrt(b^2)

        if (magnitude1 != 0.0 | magnitude2 != 0.0) {
            cosineSimilarity = dotProduct / (magnitude1 * magnitude2);
        } else {
            return 0.0;
        }
        return cosineSimilarity;
    }

    /**
     * Calculates the tf of a term
     *
     */
    public static double tfCalculator(double termCount, double totalterms) {

        return termCount / totalterms;
    }

    /**
     * Calculates idf of a term
     */
    public static double idfCalculator(HashMap<String, Double> allTermCounts,
                                       double totaldocs, String termToCheck) {

        //TODO: put the IDF score from a bigger internet corpus/crawl

        if(allTermCounts.containsKey(termToCheck))
            return 1 + Math.log(totaldocs / allTermCounts.get(termToCheck));
        else
            return 1 ;
    }

    /**
     * Calculates the tf-idf of a new doc, but does not store anything into to the
     * knowledgebase
     *
     * @param doc
     */
    public static HashMap<String, Double> tfIdfCalculator(String[] doc) {
        double tf; // term frequency
        double idf; // inverse document frequency
        double tfidf; // term requency inverse document frequency
        HashMap<String, Double> vector = new HashMap<String, Double>();
        HashMap<String, Double> termCount = new HashMap<String, Double>();

        // calculate the termcounts for this doc

        for (String word : doc) {
            updateMap(word, termCount, 1);
        }

        for (String word : termCount.keySet()) {
            tf = tfCalculator(termCount.get(word), doc.length);
            idf = idfCalculator(allTermCounts, totaldocs, word);
            tfidf = tf * idf;
            vector.put(word, tfidf);

        }
        return vector;

    }

    /**
     * Calculates the average cosine similarity between a given document and all
     * the docs/vectors in the knowledge base
     */
    public static double getCosineSimilarity(HashMap<String, Double> vector, int of) {

        double avgmax = 0.0;
        double avgmin=0.0;
        double avgdiff=0.0;

        ArrayList<Double> rankedscores=new ArrayList<Double>();
        if(of==-1){
            of=vectors.size();
        }


        for (HashMap<String, Double> vec : vectors) {
            double score = cosineSimilarity(vec, vector);
            rankedscores.add(score);
            //System.out.println("Score "+score);
        }
        Collections.sort(rankedscores);


        for(int i =vectors.size()-1;i>=vectors.size()-of;i--){
            avgmax+=rankedscores.get(i);
        }

        for(int i =0;i<of;i++){
            avgmin+=rankedscores.get(i);
        }

        avgdiff=avgmax-avgmin;

        //System.out.println("avgmax: "+avgmax/of);
        //System.out.println("avgmin: "+avgmin/of);
        //System.out.println("avgdiff: "+avgdiff/of);

        return (avgmax / of);

    }

    /**
     * stores one doc/vector in the vector knowledge base and update the idf kb as well
     *
     * @param docs
     * @throws FileNotFoundException
     * @throws IOException
     */
    public static void parseFile(List<String> docs) throws IOException {

        addIdfKb(docs);

        for(String doc:docs){
            String[] tokenizedTerms = tokenizeintoBOW(STOP_WORDS, doc, LangParser.posTagger);
            vectors.add(tfIdfCalculator(tokenizedTerms));
        }


    }


    /**
     * Adds to the part of kb that's used for idf calculation (idf kb) but does not add to the kb vectors
     * @throws IOException
     */
    public static void addIdfKb(String doc) throws IOException{



        String[] tokenizedTerms = tokenizeintoBOW(STOP_WORDS, doc, LangParser.posTagger);

        for (String word : tokenizedTerms) {
            updateMap(word, allTermCounts, 1);

        }
        totaldocs++;
    }



    /**
     * Adds multiple docs to the part of kb that's used for idf calculation but does not add to the kb vectors
     * @throws IOException
     */
    public static void addIdfKb(List<String> docs) throws IOException{

        for(String doc:docs){

            addIdfKb(doc);
        }
    }

    public static void main(String[] args) throws FileNotFoundException, IOException {


        ArrayList<String> kb=new ArrayList<String>();
        kb.add("how are you doing my friend i am doing");
        kb.add("you are my good boy i am doing");
        kb.add("i am doing just fine");



        String test="i am doing just fine";
//		test=test.toLowerCase();
//
//		String taggerPath = "edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger";
//		MaxentTagger tagger = new MaxentTagger(taggerPath);
//		String text="How are you doing my Friend ? You are my good boy. They said they will go to the World Tour.";
//		String[] bow=tokenizeintoBOW("/Users/asitangmishra/Desktop/JPL/files/internet-stopwords", text, tagger);
//
//		for(String word:bow){
//		System.out.println(word);
//		}
//

        parseFile(kb);

        for(HashMap<String, Double> vector:vectors){


            for(String key:vector.keySet()){
                System.out.println(key+":"+vector.get(key));
            }
            System.out.println("\n");
        }


        HashMap<String, Double> tempvector	=tfIdfCalculator(tokenizeintoBOW("/Users/karanjeetsingh/asitang/internet-stopwords", test, LangParser.posTagger));

        for(String key:tempvector.keySet()){
            System.out.println("tempvector "+key+":"+tempvector.get(key));
        }

        double result=getCosineSimilarity(tempvector,3);

        System.out.println(result);





    }


    public static void printAllTermsMap() {
        TreeMap<String, Double> map = new TreeMap<String, Double>(Collections.reverseOrder());
        map.putAll(allTermCounts);

        List<Entry<String, Double>> sortedEntries = new ArrayList<Entry<String, Double>>(map.entrySet());

        Collections.sort(sortedEntries, new Comparator<Entry<String, Double>>() {
            @Override
            public int compare(Entry<String, Double> e1, Entry<String, Double> e2) {
                return e2.getValue().compareTo(e1.getValue());
            }
        });

        for (Iterator<Map.Entry<String, Double>> it = sortedEntries.iterator(); it.hasNext();) {
            Map.Entry<String, Double> entry = it.next();
            System.out.println(entry.getKey() + " - " + entry.getValue());
        }
    }

}
