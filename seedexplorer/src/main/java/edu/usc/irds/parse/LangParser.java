package edu.usc.irds.parse;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ie.crf.CRFClassifier;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.nndep.DependencyParser;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.util.StringUtils;

/**
 * A utility class for Language Processing.
 * Uses Stanford Core NLP and NER
 * @author asitangmishra
 * @modified_by karanjeetsingh
 */
public class LangParser {

    private static final String DEFAULT_POS_MODEL = "edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger";
    private static final String DEFAULT_NER_MODEL = "edu/stanford/nlp/models/ner/english.conll.4class.distsim.crf.ser.gz";
    private static final String DEFAULT_PARSER_MODEL = DependencyParser.DEFAULT_MODEL;

    public static final List<String> DEFAULT_OPS = new ArrayList<String>();

    public static MaxentTagger posTagger;
    public static AbstractSequenceClassifier nerClassifier;
    public static DependencyParser parser;

    static {
        posTagger = new MaxentTagger(DEFAULT_POS_MODEL);
        nerClassifier = CRFClassifier.getClassifierNoExceptions(DEFAULT_NER_MODEL);
        parser = DependencyParser.loadFromModelFile(DEFAULT_PARSER_MODEL);
        DEFAULT_OPS.add("NN");
        DEFAULT_OPS.add("JJ");
        DEFAULT_OPS.add("NNS");
        DEFAULT_OPS.add("NNP");
    }

    /**
     * This method makes clusters of words to create noun phrases
     * @param op : The list of kind of pos tags you want to put in the island
     * @param td
     * @param gs
     * @return
     */
    public static List<ArrayList<TypedDependency>> makeIslands(
            List<String> op, List<TypedDependency> td,
            GrammaticalStructure gs) {
        boolean lastflag = false;
        IndexedWord lastword = null;
        TypedDependency lastdepend=null;
        ArrayList<TypedDependency> island = null;
        ArrayList<ArrayList<TypedDependency>> master = new ArrayList<ArrayList<TypedDependency>>();
        master.add(null);
        int previndex = 0;

        for (TypedDependency t : td) {
            if (t.dep().index() == previndex) // do not process a dep with
                // multiple incoming edges (or will create a loop)
                continue;


            // if the word contains relevant tags: put into islands
            if (op.contains(t.dep().tag().toString())) {
                if (!lastflag) { //last words was not a relevant tag: so start a new island
                    island = new ArrayList<TypedDependency>();
                    // special case: check before making a new island: if the previous word was an adjective modifier
                    if (lastword != null
                            && (lastword.tag().equals("VBN") || lastword.tag()
                            .equals("ADJ"))
                            && (gs.getGrammaticalRelation(t.dep(), lastword)
                            .toString().equals("amod"))) {
                        //add the previous word
                        island.add(lastdepend);
                        master.add(lastword.index(), island); //Note: each word index contain now the location of the island it belongs to
                    }
                    //now add the current word
                    island.add(t);
                    master.add(t.dep().index(), island);
                    lastflag = true;
                    lastword = t.dep();
                    lastdepend=t;
                }

                else { //last words was a relevant tag: add the current word to the last island
                    island.add(t);
                    master.add(t.dep().index(), island);
                    lastword = t.dep();
                    lastdepend=t;
                    lastflag = true;

                }

            }
            // if the word contains irrelevant tags
            else {
                lastflag = false;
                lastword = t.dep();
                master.add(t.dep().index(), null); //adding null to that word index position, as it has no island to belong to
                lastdepend=t;
            }

            previndex = t.dep().index();

        }

        return master;
    }

    /**
     * Detects location in a sentence using Stanford NER Classifier
     * @param sentence
     * @return
     */
    public static List<String> getLocations(List<HasWord> sentence) {
        List<String> locations = new ArrayList<String>();
        List<CoreLabel> out = nerClassifier.classifySentence(sentence);
        for (CoreLabel word : out) {
            //System.out.println(word.get(CoreAnnotations.AnswerAnnotation.class));
            if(word.get(CoreAnnotations.AnswerAnnotation.class).equals("LOCATION")) {
                locations.add(word.word().trim());
            }
        }
        return locations;
    }


    public static boolean isLocation(CoreLabel word) {
        return word.get(CoreAnnotations.AnswerAnnotation.class).equals("LOCATION");
    }


    /**
     * Detects location in a sentence using Stanford NER Classifier
     * Join the locations which are together with no spaces
     * @param sentence
     * @return
     */
    public static LinkedHashSet<String> getFormattedLocations(List<HasWord> sentence) {
        LinkedHashSet<String> locations = new LinkedHashSet<String>();
        LinkedHashSet<String> subLocation = new LinkedHashSet<String>();
        List<CoreLabel> out = nerClassifier.classifySentence(sentence);

        for(int i = 0; i < out.size(); i++) {
            CoreLabel word = out.get(i);

            if(!isLocation(word) && subLocation.size() > 0) {
                locations.add(StringUtils.join(subLocation, " "));
                subLocation = new LinkedHashSet<String>();
            }

            if(isLocation(word))
                subLocation.add(word.word().trim());
        }

        return locations;
    }


    /**
     * Does POS tagging on the sentence
     * @param sentence
     * @return
     */
    public static List<TaggedWord> posTagging(List<HasWord> sentence) {
        return posTagger.tagSentence(sentence);
    }

    /**
     * Retrieves the parse tree from a tagged sentence
     * @param taggedSentence
     * @return
     */
    public static ArrayList<TypedDependency> getDependencyTree(List<TaggedWord> taggedSentence) {
        GrammaticalStructure gs = parser.predict(taggedSentence);
        return (ArrayList<TypedDependency>)gs.typedDependenciesCollapsedTree();
    }

    /**
     * Retrieves the parse tree from a grammatical structure
     * @param gs
     * @return
     */
    public static ArrayList<TypedDependency> getDependencyTree(GrammaticalStructure gs) {
        return (ArrayList<TypedDependency>)gs.typedDependenciesCollapsedTree();
    }

    /**
     * Retreives the Grammatical Structure of a tagged sentence
     * @param taggedSentence
     * @return
     */
    public static GrammaticalStructure getGrammarStructure(List<TaggedWord> taggedSentence) {
        return parser.predict(taggedSentence);
    }


    public static void main(String[] args) {

    }

}
