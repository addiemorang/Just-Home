import os
import csv
from django.http import HttpResponseRedirect

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'Just-Home/Just-Home/cred.json'

class LeaseTranslater():

    def translate_pdf(self, pdf_name):
        user_lang = input("What language would you like to translate your lease to? ")
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


    def get_language_dict(self):
        with open('languages.csv', mode='r') as infile:
            reader = csv.reader(infile)
            lang_dict = {rows[0]:rows[1] for rows in reader}
        return lang_dict
