# ISO4 Abbrevations Expander
This is a simple commandline tool for expanding journal name abbreviations. 

Journal name abbreviations standards are denoted here by "List of Title Word Abbreviations": https://www.issn.org/services/online-services/access-to-the-ltwa/

I stumbled upon this problem when I was looking through Wikipedia Citations and realized that I sometimes cannot understand the abbreviated names of journals. As I searched for tools that tackles this issue, I found many resources that can abbreviate journal names but no notable ones that goes in the other direction of exanding out abbreviations. I understand that this stems from the fact that abbreviations often takes the stem such that many full words will abbreviate to the same shortened form, not including complications that arise with different languages. So this project is my attempt to recover lost semantic meaning by using data points to train models which examine frequency relationships between words. 

This project is a still a working progress. Feel free to contact if you have any suggestions or concerns!

# Installation
## Manual
Downloading Repository
```bash
  $ git clone https://github.com/graceCXY/iso4-abbrev-expander.git
```
Setting up the environment
```bash
  $ python3 -m venv abbrev-env
  $ source abbrev-env/bin/activate
```
Getting all the dependencies from requirements.txt
```bash
  $ pip install -r requirements.txt
```

# Usage
## Abbreviate
`abbreviate <FullName>`
```bash
$ python deabbreviate/__main__.py abbreviate "Journal of Earthquake Engineering"
"J. Earthq. Eng."
```
## Expand
`expand <AbbrevName>`
```bash
$ python deabbreviate/__main__.py expand "J. Earthq. Eng."
"Journal of Earthquake Engineering"
```
# Limitations 
## Input Data Format 
The input data expansion must be in the format such that there is a "." behind every abbreviated word as per ISO4 standards. For instance, "J Earthq Eng" 

## Training Data
Since this model it built on probabilities and frequencies, it highly relies on the training data it receives and is also limited by common mistakes and tendencies of the training data. Currently, I use the csv files listed here https://github.com/JabRef/abbrv.jabref.org/tree/master/journals.

## Languages 
Adding on to the previous limitation regarding training data, some abbreviations can seems like it is from English when if fact, it is from different languages. Since, the training data skew towards english, if the user knows of the original language of the full name, a 3-digit code of the language should be provided.



# How it works
As a visual learner, I made a diagram to demonstrate the workflow of the program. 
![alt text](https://github.com/graceCXY/iso4-abbrev-expander/blob/master/deabbreviate/workflow_diagram.png)

Language detection: Given a abbreviated journal name, we try to determine its language if none was given. Due to the library used, the output of language detection would be a 2 character code.

Tokenization: We then tokenize the entire journal name to a list of abbreviated words. 

For each of the words


# Challenges and Future Research
Due to my time limitations, the project remains a working progress. There are many areas of the project that yet needs to be improved. Some of the areas I'm considering include: 

### Part of Speech Patterns 
I can improve the existing part of speech analysis module such that it helps the program makes a more informed decision based on language patterns. For instance, in English, normally 3 nouns would not be seen in a row and in this situation, perhaps the program can observe other relevant choices of an abbreviation expansion. 

In addition, perhaps part of speech analysis of patterns for titles can provide some insights into the inclusion of articles, specifically that of the article "the". This is an particular fascinating area of exploration for me because sometimes phrasing that appears intuitive to humans seem to be spontaneous patterns to computers and it would be interesting to attempt to bridge this gap.  

### Improved Training Data
As mentioned before, the current workflow relies heavily on the training data so improving the quality of the training data can definitely improve the accuracy for the model. For instance, some entries in the data do not have "." included in abbreviated work and thus would not be processed accordingly due to limitations to the model. 

In addition, the program works the best with English and having more data of different languages and possibly noting down what these langauges are can potentially normalize the skew. 

### Robust Testing Mechanism 
The testing mechanism can also be more robust since following the addition of more training data, more can thus be allocated to testing. 

### Experiment with Different Models
I can experiment with different layers of the existing program. For example, there may be some redundancies in the existing most frequent column calculation and the frequency column that affects the runtime efficiency of the program. We can potentially combine the verfication step of these two columns with the raw expansions as a design choice. 

In addition, there are many possibilities with Machine Learning that I have not explored. I can potentially incorporate many existing tools and algorithms into this design given more time :) 

