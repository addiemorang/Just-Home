import PyPDF2
import nltk
import numpy as np
from nltk.corpus import brown, stopwords
from nltk.cluster.util import cosine_distance
from operator import itemgetter
import re
from google.cloud import translate
import os
import csv

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/Users/addiemorang/Documents/GitHub/addiemorang.github.io/tech_together/cred.json'

def translate_pdf(pdf_name):
    user_lang = (input("What language would you like to translate your lease to? ")).lower()
    lang_dict = get_language_dict()
    try:
        lang_code = lang_dict.get(user_lang)
        pdf_sents = get_text_from_lease(pdf_name)
        translated_file = open('translated.txt', "w")
        client = translate.Client()
        for s in pdf_sents:
            print('writing...')
            translated_file.write(client.translate(s, source_language='en', target_language=lang_code)['translatedText'])

    except:
        print("Error: language not found/supported.")


def get_language_dict():
    with open('languages.csv', mode='r') as infile:
        reader = csv.reader(infile)
        lang_dict = {rows[0].lower():rows[1].lower() for rows in reader}
    return lang_dict


np.seterr(divide='ignore', invalid='ignore')

def pagerank(A, eps=0.0001, d=0.85):
    if len(A) > 0:
        P = np.ones(len(A)) / len(A)
    while True:
        new_P = np.ones(len(A)) * (1 - d) / len(A) + d * A.T.dot(P)
        print(new_P)
    #    new_P = .001
        delta = abs(new_P - P).sum()
        if delta <= eps:
            return new_P
        P = new_P

def sentence_similarity(sent1, sent2, stop_words=stopwords.words('english')):

    if stop_words is None:
        stop_words = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stop_words:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stop_words:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words=stopwords.words('english')):
    # Create an empty similarity matrix
    S = np.zeros((len(sentences), len(sentences)))
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:
                continue
            S[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    # normalize the matrix row-wise
    for idx in range(len(S)):
        if S[idx].sum() == 0:
            continue
        else:
            S[idx] /= S[idx].sum()
    return S


def text_rank(sentences, top_n = 20, stop_words=stopwords.words('english')):
    """
    sentences = a list of sentences [[w11, w12, ...], [w21, w22, ...], ...]
    top_n = how may sentences the summary should contain
    stopwords = a list of stopwords
    """
    S = build_similarity_matrix(sentences, stop_words)
    sentence_ranks = pagerank(S)

    # Sort the sentence ranks
    ranked_sentence_indexes = [item[0] for item in sorted(enumerate(sentence_ranks), key=lambda item: -item[1])]
    selected_sentences = sorted(ranked_sentence_indexes[:top_n])
    summary = itemgetter(*selected_sentences)(sentences)
    return summary


def split_sentences(text):
    text = text.replace('™', '')
    text = text.replace('.', '. ')
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = sent_detector.tokenize(text.strip().replace('\n', ''))
    return sentences

def get_text_from_lease(pdf_name):
    pdf = open('blanklease.pdf', 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf)
    num_pages = pdf_reader.numPages
    lease_text = ''
    for i in range(num_pages):
        lease_text += pdf_reader.getPage(i).extractText()
    sentence_list = split_sentences(lease_text)
    return sentence_list


#TODO: clean \n characters, weird special characters, deal w weird symbol thing??
def clean_text(): # returns cleaned up version of text
    return 0

def search_phrase(text, phrase):
    found = []
    result = re.search(phrase, text)
    if (result is not None):
        found.append(result.string)
    return found

if __name__ == "__main__":
    pdf_name = input("what is the filepath of your pdf lease document? ")
    #sentences = get_text_from_lease(pdf_name)
    #num = int(input("how many sentences do you want in your lease summary? "))
    #for idx, sentence in enumerate(text_rank(sentences, stop_words=stopwords.words('english'), top_n = num)):
    #    print("%s. %s" % ((idx + 1), ''.join(sentence)))

    dict_syn = {'tenant':'lessee',
        'lessee': 'tenant',
        'landlord': 'property owner',
        'property owner' : 'landlord',
        'landlord': 'proprietor',
        'proprietor':'landlord',
        'landlord':'freeholder',
        'freeholder':'landlord',
        'dweller':'tenant',
        'tenant': 'dweller',
        'holder':'tenant',
        'tenant':'holder',
        'inhabitant':'tenant',
        'tenant':'inhabitant',
        'occupant':'tenant',
        'tenant':'occupant',
        'renter':'tenant',
        'tenant':'renter',
         'tenant':'resident',
         'resident': 'tenant',
         'leaseholder':'tenant',
         'tenant':'leaseholder'}

    dict_categories = {'hold landlord harmless': 'liability',
        'tenant shall indemnify': 'liability',
        'no implied warranty': 'liability',
        'tenant accepts the unit': 'habitability',
        'accepts unit as is':'habitability',
        'unit as is condition':'habitability',
        'tenant warrants habitable condition': 'habitability',
        'no warranty of habitability':'habitability',
        'upon payment of sums':'habitability'}

    #for c in dict_categories:
    #    phrase = c
    #    sample = 'include a clause which exculpates or indemnifies the landlord from any and all liability, for example, by providing that “the tenant shall indemnify and hold landlord harmless from any and all claims or assertions of every kind and nature.'
    #    if (len(search_phrase(sample,phrase))>0):
    #        print(search_phrase(sample,phrase))

    translate_pdf(pdf_name)
