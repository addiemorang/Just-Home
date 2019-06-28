# ivonne was here
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

np.seterr(divide='ignore', invalid='ignore')

def page_rank(A, eps=0.0001, d=0.85):
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
    num_violations = 0
    violation_map = {'liability': [], 'habitability':[], 'quiet enjoyment':[], 'maintenance':[], 'payment':[], 'termination':[], 'entry':[]}
    for sentence in sentences:
        for phrase, category in dict.items():
            contains_phrase = search_phrase(sentence, phrase)
            if contains_phrase:
                num_violations += 1
                violation_map[category].append(sentence)
    return violation_map, num_violations

def clarify_rights(violations, num_violations):
    response = 'SUMMARY OF YOUR RIGHTS AS A TENANT:\n'
    response += 'We have reviewed your lease for possible violations in the following categories: \n(1) Landlord’s liability for loss or damage \n(2) The Warranty of Habitability\n(3) The Covenant on Quiet Enjoyment \n(4) Maintenance and Repair \n(5) Payments and Fees \n(6) Termination of Tenancy and Eviction \n(7) Landlord’s Right of Entry\n\n'
    response += 'Your lease looks'
    if num_violations == 0:
        response += ' good, as far as we can tell, with no obvious legal violations. Still, let\'s review your rights!\n'
    elif num_violations < 3:
        response += ' ok, with 1-2 possible legal violations. Let\'s review your rights as a tenant!\n'
    else:
        response += ' poor, with more than 3 possible legal violations. Let\'s review your rights as a tenant!\n'

    ############
    response += '\n(1) LANDLORD\'S LIABILITY FOR LOSS OR DAMAGE'
    response += '\nG.L.c. 186, §15 prohibits a landlord from waiving her liability for injuries, loss or damage, caused to tenants or third parties by her negligence, omission, or misconduct.\n'
    if violations['liability'] != []:
        response += '\tYour lease may contain a waiver of your landlord\'s liability for damages.'
        response += '\tCheck the following passage(s) for possible violations:\n'
        for passage in violations['liability']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += '\tYour lease does not seem to absolve the landlord of all liability for damage, which is good!\n\n'
    ###########
    response += '(2) WARRANTY OF HABITABILITY\n'
    response += '\nIn its landmark decision in Boston Housing Authority v. Hemingway, the Massachusetts Supreme Judicial Court determined that when a landlord rents a residential unit under a written or oral lease, she makes an “implied warranty that the premises are fit for human occupation.\n'
    if violations['habitability'] != []:
        response += '\tYour lease may contradict the warranty of habitability, either by asking you, the tenant, to verify that the apartment is fit for habitation (while really the landlord must agree to this), or in another way. Check the below passage(s) for possible violations:\n'
        for passage in violations['habitability']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease does not appear to contradict the warranty of habitability. (Note that even if it is not explicitly stated, it is implied under MA law). When your landlord rents to you, they are making an implied warranty that the premises are fit for human occupation and that there are no health and safety violations at the time of rental.\n'
    response += 'Since the warranty of habitability legally holds for all leases in MA. If your landlord does not keep your apartment in livable condition they have broken the warranty of habitation, and you may pursue legal action. See more info here: https://www.masslegalhelp.org/housing/lt1-chapter-13-filing-civil-lawsuit. \n'

    ##########
    response += '\n(3) COVENANT ON QUIET ENJOYMENT'
    response += '\nAccording to the Supreme Judicial Court of Massachusetts in Simon v. Solomon, the phrase \'quiet enjoyment\' signifies \'the tenant’s right to freedom from serious interferences with his tenancy — acts or omissions that \'impair the character and value of the leased premises.\"  G.L.c.186, §14 penalizes any landlord who willfully fails to furnish water, hot water, heat, light, power, gas or other services, as required by law or contract; who directly or indirectly interferes with the furnishing of utilities or services or with the quiet enjoyment of any occupant in the premises; or who attempts to regain possession of such premises by force without judicial process. The section also prohibits a landlord from taking reprisals against a tenant who reports or issues proceedings against a breach of the covenant of quiet enjoyment. Eviction by the landlord, whether actual or constructive (i.e., any violation of landlord’s duties which effectively deprives the tenant of her enjoyment of the premises), constitutes a breach of the covenant of quiet enjoyment. Such a breach will entitle the tenant to triple damages or three months\' rent (whichever is greater), as well as costs and attorney\'s fees. This covenant cannot be waived by the parties.\n'
    if violations ['quiet enjoyment'] != []:
        response += 'Your lease may wrongfully imply that the covenant of quiet enjoyment is contingent on the behavior of tenant, non-payment of rent, or any other action of the tenant. Check the below passage(s) for possible violations: \n'
        for passage in violations['quiet enjoyment']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease does not appear to contain language regarding the covenant of quiet enjoyment. In the absence of specific language, your rights to quiet enjoyment are implied under MA law.\n'

    ##########
    response += '\n(4) MAINTENANCE AND REPAIR'
    response += '\nThe landlord\'s and tenant\'s maintenance and repair responsibilities are mandated by the State Sanitary Code. The Code places most of the burden of providing and maintaining the premises in safe and habitable condition on the landlord, while imposing only minimal maintenance obligations on the tenant. The landlord\'s duties include, inter alia, providing and maintaining in good operating condition the water-heating facilities, electrical facilities, drinkable water, toilet and a sewage disposal system, and locks on entry doors. The landlord further bears responsibility to maintain structural elements in \"good repair and in every way fit for the use intended\"; and to install and \"maintain free from leaks, obstructions or other defects\" sinks, bathtubs, toilets, gas and water pipes, and other fixtures supplied by the landlord. Lastly, the landlord has an obligation to exercise reasonable care to ensure that the common areas under her control are reasonably well maintained(88). The tenant, on the other hand, only needs to “maintain free from leaks, obstructions and other defects\" all \"occupant owned and installed equipment\" (89); to maintain “in a clean and sanitary condition […] that part of the dwelling which he exclusively occupies or controls\"; and to \"exercise reasonable care\" in the use of the structural elements of the dwelling(91). Tenant\'s benefits, as set forth by the State Sanitary Code, cannot be waived under any residential lease. Finally, the State Sanitary Code includes a “repair and deduct” statute, aimed at enabling tenants to enforce landlords\' compliance with the Code(93). It offers the tenant the ability to make repairs and lawfully deduct the cost incurred from the rent or, alternatively, to treat the lease as abrogated and vacate the premises within a reasonable time(94). These benefits cannot be waived by the parties.\n'
    if violations ['maintenance'] != []:
        response += 'Your lease may be neglecting to state the landlord’s duties. Check the below passage(s) for possible violations: \n'
        for passage in violations['maintenance']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease does not appear to be neglecting to state the landlord’s duties. However, some leases subject the landlord’s and tenant’s obligations to applicable law, after misstating the division of duties by placing all of the repair duties on the tenant. Make sure that your lease contains an enforceable maintenance and repair clause.\n'

    #############
    response += '\n(5) PAYMENT AND FEES'
    response += '\nMA statutes prohibit landlords from requiring, at or prior to the commencement of the tenancy, any amount in excess of the first month’s rent, the last month’s rent, a security deposit equal to the first month’s rent, and the purchase and installation cost for a key and lock. Failure to comply with this provision constitutes “unfair or deceptive act.”\n'
    if violations ['payment'] != []:
        response += 'Your lease may contain unenforceable clauses, which either require a security deposit in an amount higher than the first month’s rent, or include “extra fees” (such as: “move-in” and “move-out” non-refundable fees, a cleaning deposit, and a “onetime” fee).\n'
        response += 'Interest for the Last Month\'s Rent: The rules on the payment of interest for the last month’s rent are pretty straightforward: a landlord who receives rent in advance for the last month of the tenancy is obliged to give the tenant a receipt, and a statement indicating that the tenant is entitled to interest on the said rent payment. If the landlord fails to pay interest on the last month’s rent, the tenant is entitled to damages.\t Security Deposit: The landlord is required, inter alia, to provide the tenant with a receipt; to deposit and hold the funds in a separate, interest-bearing, account; and to return the deposit with interest, less lawful deductions, within 30 days after the termination of the tenancy. The landlord may only deduct from the deposit for the expenses listed in the statute, and pursuant to furnishing to the tenant an itemized list of the damages. Failure to “state fully and conspicuously in simple and readily understandable language” one of these issues is an “unfair or deceptive practice.\”\tLate Payments: MA landlord and tenant laws do not prohibit or cap late charges or interest in a residential lease, but require that such fees will be imposed only after the default has lasted for at least 30 days.\tAttorney\'s Fees: MA General Laws provide that if a residential lease entitles the landlord to recover attorney’s fees and expenses if when prevailing in a suit, the tenant shall have the same right if she prevails against the landlord. In other words, the courts are required by statute to interpret one-sided attorney’s fees clauses as a mutual obligation to pay the costs of the prevailing party. Any lease agreement that waives the right of the tenant to recover attorney’s fees and expenses in these circumstances is void and unenforceable. Check the below passage(s) for possible violations:\n'
        for passage in violations['payment']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease does not seem to contain any unenforceable clauses.\n'

    #############
    response += '\n(6) TERMINATION OF TENANCY AND EVICTION'
    response += '\nSince 1969, a landlord is required to give a 14 days’ notice in writing before terminating the lease due to non-payment of rent. A landlord is also prohibited from waiving the tenant’s right to cure the nonpayment by paying the amount owed within the statutory reinstatement period.\n'
    if violations['termination'] != []:
        response += 'Your lease may violate the clause that 14 days notice are needed in the event of a landlord wishing to evict you for non-payment of rent. Your lease may be omitting the information that you can stop any eviction by paying the amount of rent owed before the 14 day period you are given is over. Be aware of this even if it is not mentioned in your lease! Check the below passage(s) for possible violations:\n'
        for passage in violations['termination']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease appears to fully inform you of your right to a 14 day period before your tenancy terminates in the event of an attempted eviction. However, your lease may be omitting the information that you can stop any eviction by paying the amount of rent owed before the 14 day period you are given is over. Be aware of this even if it is not mentioned in your lease!\n'

    ##########
    response += '\n(7) LANDLORD\'S RIGHT OF ENTRY'
    response += '\nThe MA Legislature chose to restrict the landlord\'s right of access to the premises for the limited purposes set forth in the statute: to inspect the premises, make repairs, or show them to a prospective tenant, purchaser, mortgagee or its agents.\n'
    if violations ['entry'] != []:
        response += 'Your lease may violate MA law by stating your landlord can enter your apartment for any reason. See below: \n'
        for passage in violations['entry']:
            response += '*** \"' + passage + '\" ****\n'
    else:
        response += 'Your lease appears to follow MA law by stating that your landlord needs permission to enter your premises and for limited purposes.\n'

    return response


if __name__ == "__main__":
    pdf_name = input("what is the filepath of your pdf lease document? ")
    translate_pdf(pdf_name)
    sentences = get_text_from_lease(pdf_name)
    num = 10 # number of summary points
    summary = '\n\n\nSUMMARY OF IMPORTANT PARTS OF YOUR LEASE:\n '
    for idx, sentence in enumerate(text_rank(sentences, stop_words=stopwords.words('english'), top_n = num)):
        summary += '(' + str(idx+1) + ') ' + sentence + '\n'
    summary += '\n\n'

    dict_categories = {'hold landlord harmless': 'liability',
        'hold the landlord harmless': 'liability',
        'tenant shall indemnify': 'liability',
        'no implied warranty': 'liability',
        'tenant accepts the unit': 'habitability',
        'accepts unit as is':'habitability',
        'unit as is condition':'habitability',
        'tenant warrants habitable condition': 'habitability',
        'no warranty of habitability':'habitability',
        'upon payment of sums':'habitability',
        'landlord harmless from claims': 'liability',
        'observance of all rules':'quiet enjoyement',
        'observance of all regulations': 'quiet enjoyement',
        'tenant performance of agreement':'quiet enjoyement',
        'may peacefully and quietly': 'quiet enjoyement',
        'enjoy premises for term': 'quiet enjoyement',
        'tenant failure to pay':'quiet enjoyement',
        'not obligated to repair': 'maintenance',
        'no obligations for maintenance': 'maintenance',
        'are not landlord resposibility':'maintenance',
        'tenant needs to fix':'maintenance',
        'tenant does all repairs':'maintenance',
        'tenant does apartment maintenance':'maintenance',
        'termination will become effective':'termination',
        'enter apartment without permission':'entry',
        'enter apartment without notice':'entry',
        'tenant pays all damage':'maintenance',
        'pay damage above wear': 'maintenance',
        'at its sole expense': 'maintenance',
        'maintain premises and appurtenances':'maintenance',
        'in addition to rent':'maintenance',
        'wear tear unavoidable casualty':'maintenance',
        'landlord may make repairs':'maintenance',
        'tenant shall reimburse landlord':'maintenance',
        'reimburse landlord for repairs':'maintenance',
        'reimburse landlord in full':'maintenance',
        'reimburse cost any repairs':'maintenance',
        'pay move-in fees':'payment', 'pay move-out fees':'payment',
        'pay non-refundable fees':'payment',
        'pay a cleaning deposit':'payment', 'pay a onetime fee':'payment',
        'deposit returned without interest':'payment',
        'pay reasonable attorney fee': 'payment'
    }

    violations, num_violations = find_violations(sentences, dict_categories)
    response = clarify_rights(violations, num_violations)

    text_file = open("output.txt", "w")
    text_file.write(summary)
    text_file.write('\n')
    text_file.write(response)
    text_file.close()
        #search_phrase(sample,phrase)
