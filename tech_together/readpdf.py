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
num_violations = 0

def pagerank(A, eps=0.0001, d=0.85):
    if len(A) > 0:
        P = np.ones(len(A)) / len(A)
    while True:
        new_P = np.ones(len(A)) * (1 - d) / len(A) + d * A.T.dot(P)
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
    pdf = open(pdf_name, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf)
    num_pages = pdf_reader.numPages
    lease_text = ''
    for i in range(num_pages):
        lease_text += pdf_reader.getPage(i).extractText().replace('lessor', 'landlord').replace('Lessor', 'landlord').replace('lessee', 'tenant').replace('Lessee', 'tenant')
    sentence_list = split_sentences(lease_text)
    return sentence_list


#TODO: clean \n characters, weird special characters, deal w weird symbol thing??
def clean_text(): # returns cleaned up version of text
    return 0

def search_phrase(text, phrase):
    found = []
    result = re.search(phrase, text)
    if (result is not None):
        return True
        #print(result.string)
    return False

def find_violations(sentences, dict):
    violation_map = {'liability': [], 'habitability':[], 'quiet enjoyment':[], 'maintenance':[], 'payment':[], 'termination':[], 'right to enter':[]}
    for sentence in sentences:
        for phrase, category in dict.items():
            contains_phrase = search_phrase(sentence, phrase)
            if contains_phrase:
                num_violations += 1
                violation_map[category].append(sentence)
    return violation_map

def clarify_rights(violations):
    response = 'Newsflash: as a tenant, you have rights!\n'
    response += 'We have reviewed your lease for possible violations in the following categories: \n(1) Landlord’s liability for loss or damage \n(2) The Warranty of Habitability and the Covenant on Quiet Enjoyment \n(3) Maintenance and Repair \n(4) Payments and Fees \n(5) Termination of Tenancy and Eviction \n(6) Landlord’s Right of Entry\n\n'
    response += 'Your lease looks'
    if num_violations == 0:
        response += ' good, as far as we can tell, with no obvious legal violations. Still, let\'s review your rights!\n'
    elif num_violations < 3:
        response += ' fair, with 1-2 possible legal violations. Let\'s review your rights as a tenant!\n'
    else:
        response += ' poor, with more than 3 possible legal violations. Let\'s review your rights as a tenant!\n'


    response += '(1) LANDLORD\'S LIABILITY FOR LOSS OR DAMAGE'
    response += '\n\tG.L.c. 186, §15 prohibits a landlord from waiving her liability for injuries, loss or damage, caused to tenants or third parties by her negligence, omission, or misconduct.\n'
    if violations['liability'] != []:
        response += '\tYour lease may contain a waiver of your landlord\'s liability for damages.'
        response += '\tCheck the following passage(s) for possible violations:\n'
        for passage in violations['liability']:
            response += passage + '\n'
    else:
        response += '\tYour lease does not seem to absolve the landlord of all liability for damage, which is good!\n\n'

    response += '(2) WARRANTY OF HABITABILITY and COVENANT ON QUIET ENJOYMENT\n'
    response += '\tIn its landmark decision in Boston Housing Authority v. Hemingway, the Massachusetts Supreme Judicial Court determined that when a landlord rents a residential unit under a written or oral lease, she makes an “implied warranty that the premises are fit for human occupation.\n'
    if violations['habitability'] != []:
        response += '\tYour lease may contradict the warranty of habitability, either by asking you, the tenant, to verify that the apartment is fit for habitation (while really the landlord must agree to this), or in another way. Check the below passage(s) for possible violations:\n'
        for passage in violations['habitability']:
            response += passage + '\n'
    else:
        response += 'Your lease does not appear to contradict the warranty of habitability. (Note that even if it is not explicitly stated, it is implied under MA law). When your landlord rents to you, they are making an implied warranty that the premises are fit for human occupation and that there are no health and safety violations at the time of rental.'
    response += 'Since the warranty of habitability legally holds for all leases in MA. If your landlord does not keep your apartment in livable condition they have broken the warranty of habitation, and you may pursue legal action. See more info here: https://www.masslegalhelp.org/housing/lt1-chapter-13-filing-civil-lawsuit'

    return response


if __name__ == "__main__":
    pdf_name = input("what is the filepath of your pdf lease document? ")
    sentences = get_text_from_lease(pdf_name)
    num = int(input("how many sentences do you want in your lease summary? "))
    print('\n\n\nSummary of important parts of your lease: ')
    for idx, sentence in enumerate(text_rank(sentences, stop_words=stopwords.words('english'), top_n = num)):
        print("%s. %s" % ((idx + 1), ''.join(sentence)))

    print('\n\n')

    dict_categories = {'hold landlord harmless': 'liability',
        'hold the landlord harmless': 'liability',
        'tenant shall indemnify': 'liability',
        'no implied warranty': 'liability',
        'tenant accepts the unit': 'habitability',
        'accepts unit as is':'habitability',
        'unit as is condition':'habitability',
        'tenant warrants habitable condition': 'habitability',
        'no warranty of habitability':'habitability',
        'upon payment of sums':'habitability'
    }

    violations = find_violations(sentences, dict_categories)
    response = clarify_rights(violations)
    print(response)
        #search_phrase(sample,phrase)
