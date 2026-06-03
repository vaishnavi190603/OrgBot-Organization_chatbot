import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.metrics import edit_distance

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    for token, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_tokens.append(lemmatizer.lemmatize(token, pos))
    
    return lemmatized_tokens

def text_similarity(sentence1, sentence2):
    tokens1 = preprocess_text(sentence1)
    tokens2 = preprocess_text(sentence2)
    
    # Compute Levenshtein distance
    distance = edit_distance(tokens1, tokens2)
    
    # Normalize distance by the length of the longer sentence
    max_length = max(len(tokens1), len(tokens2))
    similarity = 1 - (distance / max_length)
    
    return similarity

sentence1 = "This is a sentence."
sentence2 = "sentense"

similarity_score = text_similarity(sentence1, sentence2)
print("Text Similarity:", similarity_score)