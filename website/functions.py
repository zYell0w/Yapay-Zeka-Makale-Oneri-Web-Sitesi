import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import nltk
import string
from nltk.stem import WordNetLemmatizer
import spacy
import fasttext
import fasttext.util
import numpy as np
from scipy.spatial.distance import cosine
from nltk.corpus import stopwords
from nltk import word_tokenize, sent_tokenize
from datasets import load_dataset
from transformers import BertTokenizer, BertModel
import pyrebase

#Firebase Config kendinize göre doldurun.
config = {
    'apiKey': "",
  'authDomain': "",
  'projectId': "",
  'storageBucket': "",
  'messagingSenderId': "",
  'appId': "",
  'databaseURL': ""}

#NLTK ve Vektör Oluşumu için indirmeler.
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
fasttext.util.download_model('en', if_exists='ignore')
ft_model = fasttext.load_model('cc.en.300.bin')
nlp = spacy.load("en_core_web_sm")

firebase = pyrebase.initialize_app(config)
authFirebase = firebase.auth()

cred = credentials.Certificate("serviceAccountKey.json Yolu BURAYI DOLDURUN!")
firebase_admin.initialize_app(cred)
db = firestore.client()

#İlgi alanı vektörlerinin oluşturulduğu yer.
def vectorGettingilgi(ilgiAlaniArray):

    ilgiAlaniArrayText = " ".join(str(element) for element in ilgiAlaniArray)
    doc = nlp(ilgiAlaniArrayText)
    finalText = []
    for token in doc:
        finalText.append(token.lemma_)

    finalTextString = " ".join(str(element) for element in finalText)
    #FastText word embedding
   
    #sentence_vector_ft = ft_model.get_sentence_vector(finalTextString)
    ArrayFtWordVectors = []
    for i in finalText:
        word_vector_ft = ft_model.get_word_vector(i)
        ArrayFtWordVectors.append(word_vector_ft)
    sentence_vector_ft = np.mean(ArrayFtWordVectors,axis=0)
    
    #SciBert text embedding
    inputs = tokenizer(finalTextString, return_tensors='pt', padding=True, truncation=True, add_special_tokens=True)
    outputs = model(**inputs)
    sentence_vector_Sci = outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy()
    
    return sentence_vector_Sci, sentence_vector_ft
def similartyIlgiVector(sci,ft):
    benzerliklerSci = []
    benzerliklerFt = []
    docs = db.collection('Assays').get()
    
    for doc in docs:
        
        assay = doc.to_dict()
        id = assay['id']
        title = assay['title']
        assayVectorSci = assay['sciVectorA']
        assayVectorFt = assay['ftVectorA']
        assayVectorSci = np.array(assayVectorSci)
        assayVectorFt = np.array(assayVectorFt)

        oranSci = 1-cosine(sci,assayVectorSci)
        oranFt = 1-cosine(ft,assayVectorFt)
        
        benzerliklerSci.append({'id' : id,'title': title, 'oranSci' : oranSci})
        benzerliklerFt.append({'id': id,'title':title,'oranFt': oranFt})
        

    benzerliklerSci.sort(key=lambda x: x['oranSci'], reverse=True)
    en_benzer_besSci = benzerliklerSci[:5]
    benzerliklerFt.sort(key=lambda x: x['oranFt'], reverse=True)
    en_benzer_besFt = benzerliklerFt[:5]
    en_benzer_besSci = benzerliklerSci[:5]
    return en_benzer_besSci,en_benzer_besFt