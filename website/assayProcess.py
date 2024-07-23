import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
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

#Bu kısım Makalelerin databaseye vektörleri ile vs kaydedilmeden önceki işlemlerin yapıldığı ardından ise kaydedildiği fonksiyon.
#Bir defa çalıştırıp makaleleri databaseye attıktan sonra kullanımına gerek yoktur.
def nlProcess(document):

    #noktalama işaretlerini kaldırmak
    document = [''.join(c for c in s if c not in string.punctuation) for s in document]
    document = [s for s in document if s]
    #stopword kelimeleri kaldırmak
    withoutStopWords = []
    for word in document:
        if word not in stop_words:
            withoutStopWords.append(word)
    withoutStopWordsText = " ".join(str(element) for element in withoutStopWords)


    doc = nlp(withoutStopWordsText)
    finalText = []
    for token in doc:
        finalText.append(token.lemma_)

    finalTextString = " ".join(str(element) for element in finalText)
    #FastText text embedding
    sentence_vector_ft = ft_model.get_sentence_vector(finalTextString)
    #SciBert text embedding
    inputs = tokenizer(finalTextString, return_tensors='pt', padding=True, truncation=True, add_special_tokens=True)
    outputs = model(**inputs)
    sentence_vector_Sci = outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy()
    return sentence_vector_Sci, sentence_vector_ft
def allDelete(db):
    docss = db.collection('Assays').get()
    for doc in docss:
        id = doc.id
        try:
            db.collection('Assays').document(id).delete()
            print(f"{id} makale silindi")
        except:
            print("hata oldu")
            exit()
    print("hepsini sildim")
    exit()

def vectorGettingilgi(ilgiAlaniArray):
    ilgiAlaniArrayText = " ".join(str(element) for element in ilgiAlaniArray)
    doc = nlp(ilgiAlaniArrayText)
    finalText = []
    for token in doc:
        finalText.append(token.lemma_)

    finalTextString = " ".join(str(element) for element in finalText)
    #FastText text embedding
    sentence_vector_ft = ft_model.get_sentence_vector(finalTextString)
    #SciBert text embedding
    inputs = tokenizer(finalTextString, return_tensors='pt', padding=True, truncation=True, add_special_tokens=True)
    outputs = model(**inputs)
    sentence_vector_Sci = outputs.last_hidden_state[:, 0, :].squeeze().detach().numpy()
 
 
    return sentence_vector_Sci, sentence_vector_ft
def AssaySaveProcess(db,dataset):
    #Data baseye datasetteki bütün makaleleri yükleme.
    for assayInfo in dataset['test']:
        document = assayInfo['document']
        document = " ".join(str(element) for element in document)
        id = assayInfo['id']
        keyWords = assayInfo['extractive_keyphrases']
        try:
            title = keyWords[0]
        except:
            first_colon = document.find(':')
            first_period = document.find('.')
        if first_colon != -1:
            title = document[:first_colon]
        elif first_period != -1:
            title = document[:first_period]
        else:
            title = "Yok"
        sciVector , ftVector = nlProcess(document)
        sciVectorA = sciVector.tolist()
        ftVectorA = ftVector.tolist()

        data = {
            'id' : f"{id}",
            'title': title,
            'document' : document,
            'keyWords' : keyWords,
            'sciVectorA' : sciVectorA,
            'ftVectorA' : ftVectorA
        }

        db.collection('Assays').document(f'{id}').set(data)
        print(f"{id} idli makale sisteme yüklenmiştir.")
    
    print("Tamami Yuklendi")

#nltk gereklilikleri.    
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')

#firebase kurulum
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

stop_words = set(stopwords.words('english'))

#datasetten veriyi çekmek için.
#dataset = load_dataset("midas/inspec", "raw")

#Eğitilmiş modellerin yüklenmesi
fasttext.util.download_model('en', if_exists='ignore')
ft_model = fasttext.load_model('cc.en.300.bin')

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

nlp = spacy.load("en_core_web_sm")
print("Modellerin yüklendi.")
