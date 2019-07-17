from joblib import load
from pathlib import Path
import string, re

def preprocess_comments(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans("","", string.punctuation))
    sentence = sentence.translate(str.maketrans("","", string.digits))
    sentence = re.sub(' +', ' ',sentence).strip()
    if sentence == "": sentence = '-'

    return sentence

def predict_sentiment(sentence):
    my_model = load(str(Path().absolute())+'/model/sentiment/model.joblib')
    word_vector = load(str(Path().absolute())+'/model/sentiment/vector.joblib')

    return str(my_model.predict(word_vector.transform([sentence]))[0])