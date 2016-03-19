<!-- 

Instruction of how to run your program.
Description of how you generated corpus.txt (e.g., manually stripped out noise, wrote a script, ran an existing tool).
Description of how you improved your program from the baseline (single word matching). You should explicitly describe what kind of new features you integrated and which examples work for your features.
Analysis of your program including weakness and strength. 

-->

# Intro

This tool is a summarizer written for Computational Linguistics (CS329) at Emory University. In this case, the program uses wikipedia articles on the last 10 presidents as a corpus. Given a search term q, the script will search the corpus and print out sentences of highest relevance.

# How to Use the Summarizer

Open your terminal and make sure you are in the directory containing `summarizer.py`, `corpus.txt.nlp`. You can read more about how to obtain corpus.txt.nlp [here](https://github.com/emory-courses/cs329/wiki/Homework-2), although it will also be discussed later in the article. 

There are two ways to use the program. There is a naive version (default) that returns all the sentences that include the given search term. In order to run this version type 
`python summarizer.py corpus.txt.nlp SEARCH-TERM` 
into your terminal and hit enter. Replace 'SEARCH-TERM' with your search term. Clearly this isn't a very good summarizer. If you would like the script to work its "summarizing magic" append the `-s` tag to the command. You can also optionally append a number after to limit the number of bullets the scrip returns. By default, the script prints the 5 most important and relevant sentences with respect to your search term. For example, if you would like to receive a 10 sentence summary on President Obama, execute the command:

`python summarizer.py corpus.txt.nlp obama -s 10`

# How to generate corpus.txt

`corpus.txt` contains the corpus of plain text used to generate (via [EmoryNLP](https://github.com/emorynlp)) `corpus.txt.nlp` (instructions [here](https://github.com/emory-courses/cs329/wiki/Homework-2)). Scraping the contents of the articles manually would be too much of a hassle so I created `scrape.py` (also in this directory) to do the heavy lifting for me. The script takes in a list of wikipedia article URLs and outputs them as plain-text to `corpus.txt`. The beauty of `scrape.py` is that it works on all wikipedia pages. `scrape.py` works as follows: 

1. Iterate through the array of wikipedia urls
2. Download their contents
3. With the help of [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/), isolate the article body (`id=mw-content-text`)
4. Iterate through all the paragraphs
5. remove the references section
6. Use soup's built in `get_text()` function to turn the HTML into plain text.
7. Remove lines not ending in a "." (some headings get through)
8. Export all lines to `corpus.txt`

# Improving the Naive Approach

## Overview

Returning a list of all sentences containing a search term is fairly trivial- simply parse the corpus into sentences, and return all those that contain the term. To make this a bit more robust, we replace the search term with its lemma. We do this by searching the corpus for all occurrences of the search term and finding the most common lemma that emoryNLP assigns to it.

The real hard part lies in improving this baseline approach to return the most important sentences containing the search term. My basic approach goes as follows:

1. Create a list of all sentences containing search term q in lemma form (already compiled through the baseline approach)
2. Assign a relevance score to each sentence
3. Print sentences with the top X scores (by default 5) in the order in which they appear in the corpus.

## Computing a sentence's score

There are two factors that contribute to a sentences score, and they rely on the following assumptions:

1. Nouns that appear more often than others do so because they are more important
2. Sentences that appear earlier than others do so because they are more important

Each sentence is assigned a `nounScore` and a `positionScore`. In order to find the `sentenceScore` we multiply `nounScore` and `positionScore`. As a result, `sentanceScore` is maximized when `nounScore` and `positionScore` are both high.

### Computing `nounScore`

A sentences `nounScore` is computed as follows:

1. For every noun that appears in the baseline, count how many total times they appear and assign the noun that score.
2. For each sentence, total the scores of all the nouns that appear in that sentence. This is the sentences `nounScore`.

For example, if 'dog' appears 35 times and 'collar' appears 10 times the sentence "The dog hates his collar" would be assigned a `nounScore` of 35.

### Computing `positionScore`

Computing `positionScore` is a lot simpler. Given the list of relevant sentences found in the baseline, a sentence's `positionScore` is equal to the length of the baseline sentences list minus its own position. For example if the baseline approach returns 10 sentences, the first sentence's score is 10, the second is 9, etc.

### Printing relevant sentences

Lastly, these two scores are multiplied, the command line arguments are parsed, and the script prints the first X sentences that have a score higher than the 5th highest score found (there were rarely every sentences with duplicate scores)

# Conclusion

This approach seems to work well. At first I didn't use `positionScore` but it ended up returning more relevant results with its inclusion. There are a few places where the program could be improved:

1. Handle phrases instead of only words
2. Replace pronouns with the nouns to which they are referring to. Sometimes its hard to tell.
3. Sometimes a noun appears a lot even though they aren't too important to the article. For example the term "President" almost always precedes the naming of a president. This can possibly be accounted for by ignoring the top X nouns with the scores.
4. Extremely long sentences have more nouns and therefore will have a higher noun score. An idea would be to find the average number of nouns that occur in each sentence (lets say 4) and only include the 4 nouns with the highest score when computing nounScore.
5. Sometimes a president is referred too a lot in an article that appears before their own, so sentences from that article shows up first













