from flask import Blueprint, render_template, request, flash, jsonify
from .auth import *
from .functions import *

#internet sitesi routing işlemlerinin olduğu yer.

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    
    if(authFirebase.current_user):
        try:
            user = db.collection('Users').document(authFirebase.current_user['email']).get()
            user = user.to_dict()
          
        except:
            return "<h1>Kullanici Bilgisi Cekilemedi</h1>"
        return render_template("home.html",currentuser = authFirebase.current_user,user = user)
    else:
        return redirect(url_for('auth.login'))

@views.route('/search/<emailAdress>',methods=['GET', 'POST'])
def search(emailAdress):

    if(authFirebase.current_user):
        
        try:
            user = db.collection('Users').document(emailAdress).get()
            user = user.to_dict()
          
        except:
            return "<h1>Kullanici Bilgisi Cekilemedi</h1>"
        
        
        if request.method == 'POST':
            arananKelime = request.form.get('aramaCubugu')

            try:
                docs = db.collection('Assays').where("keyWords", "array_contains", arananKelime).get()
                aratilmisDocs = []

                for doc in docs:
                    doc = doc.to_dict()
                    aratilmisDocs.append(doc)
                

            except:
                aratilmisDocs = []

            return render_template("search.html",currentuser = authFirebase.current_user,aratilmisDocs = aratilmisDocs)


        pass

    else:
        return redirect(url_for('auth.login'))
@views.route('/searchedAssay/<emailAdress>/<id>',methods=['GET', 'POST'])
def searchedAssay(emailAdress,id):

    if(authFirebase.current_user):
        try:
            user = db.collection('Users').document(emailAdress).get()
            user = user.to_dict()
            doc = db.collection('Assays').document(id).get()
            doc = doc.to_dict()
          
        except:
            return "<h1>Kullanici Bilgisi Cekilemedi</h1>"
        
        if request.method == 'POST':
            sci = user['ilgiSciVectorA']
            ft = user['ilgiFTVectorA']
            sci = np.array(sci)
            ft = np.array(ft)
            
            
            docSciVector = doc['sciVectorA']
            docSciVector = np.array(docSciVector)
            docFtVector = doc['ftVectorA']
            docFtVector = np.array(docFtVector)

            newVectorSci = (sci + docSciVector) / 2 
            newVectorFt = (ft + docFtVector) / 2

            newVectorSci = newVectorSci.tolist()
            newVectorFt = newVectorFt.tolist()

            vectorData = {
                'ilgiSciVectorA':newVectorSci,
                'ilgiFTVectorA': newVectorFt
            }

            try:
                db.collection('Users').document(emailAdress).update(vectorData)
            except:
                return "<h1>Guncellenemedi</h1>"

        return render_template("searchedAssay.html",currentuser = authFirebase.current_user,doc = doc)
    else:
        return redirect(url_for('auth.login'))

@views.route('/profile/<emailAdress>',methods=['GET', 'POST'])
def profile(emailAdress):

    if(authFirebase.current_user):
        
        try:
            user = db.collection('Users').document(emailAdress).get()
            user = user.to_dict()
          
        except:
            return "<h1>Kullanici Bilgisi Cekilemedi</h1>"
        
        if request.method == 'POST':
            currentUser = authFirebase.current_user
            first_name = request.form.get('firstName')
            ilgi_Alani = request.form.get('ilgiAlani')
            if not (ilgi_Alani or first_name):
                return render_template("profile.html",currentuser = authFirebase.current_user,user = user)
            
            ilgi_AlaniArray = str(ilgi_Alani).split(",")
            ilgiSciVector, ilgiFTVector = vectorGettingilgi(ilgi_AlaniArray)
            ilgiSciVectorA = ilgiSciVector.tolist()
            ilgiFTVectorA = ilgiFTVector.tolist()

            data = {
                    'email' : emailAdress,
                    'first_name' : first_name,
                    'ilgi_Alani' : ilgi_AlaniArray,
                    'ilgiSciVectorA':ilgiSciVectorA,
                    'ilgiFTVectorA':ilgiFTVectorA           
                }
            try:
                db.collection('Users').document(emailAdress).update(data)
                return redirect(url_for('views.home'))
            except:
                return "<h1>Guncellenemedi</h1>"
                
        return render_template("profile.html",currentuser = authFirebase.current_user,user = user)
    else:
        return redirect(url_for('auth.login'))
    
@views.route('/recommends/<emailAdress>',methods=['GET', 'POST'])
def recommends(emailAdress):
    if(authFirebase.current_user):
        
        try:
            
            user = db.collection('Users').document(emailAdress).get()
            user = user.to_dict()
          
        except:
            return "<h1>Kullanici Bilgisi Cekilemedi</h1>"
        
        sci = user['ilgiSciVectorA']
        ft = user['ilgiFTVectorA']
        sci = np.array(sci)
        ft = np.array(ft)
        en_benzer_besSci,en_benzer_besFt = similartyIlgiVector(sci,ft)

        sciDocsArray = []
        ftDocsArray = []
        for sciDocs in en_benzer_besSci:
            sciDoc = db.collection('Assays').document(sciDocs['id']).get()
            sciDoc = sciDoc.to_dict()
            sciDocsArray.append(sciDoc)
        
        for ftDocs in en_benzer_besFt:
            ftDoc = db.collection('Assays').document(ftDocs['id']).get()
            ftDoc = ftDoc.to_dict()
            ftDocsArray.append(ftDoc)


        if request.method == 'POST':
            listSci = []
            listFt = []
            
            for key in request.form.keys():
                value = request.form.get(key)
                if value:

                    checkBoxDoc = db.collection('Assays').document(key).get()
                    checkBoxDoc = checkBoxDoc.to_dict()
                    checkBoxDocSci = checkBoxDoc['sciVectorA']
                    checkBoxDocFt = checkBoxDoc['ftVectorA']
                
                    checkBoxDocSci = np.array(checkBoxDocSci)
                    checkBoxDocFt = np.array(checkBoxDocFt)
                    listSci.append(checkBoxDocSci)
                    listFt.append(checkBoxDocFt)
                else:
                    checkBoxDoc = db.collection('Assays').document(key).get()
                    checkBoxDoc = checkBoxDoc.to_dict()
                    checkBoxDocSci = checkBoxDoc['sciVectorA']
                    checkBoxDocFt = checkBoxDoc['ftVectorA']
                
                    checkBoxDocSci = np.array(checkBoxDocSci)
                    checkBoxDocFt = np.array(checkBoxDocFt)
                    checkBoxDocSci = checkBoxDocSci * -1
                    checkBoxDocFt = checkBoxDocFt * -1
                    listSci.append(checkBoxDocSci)
                    listFt.append(checkBoxDocFt)

            listSci.append(sci)
            listFt.append(ft)

            newSciVector = np.mean(listSci,axis=0)
            newFtVector = np.mean(listFt,axis=0)
            newSciVector = newSciVector.tolist()
            newFtVector = newFtVector.tolist()

            vectorData = {
                'ilgiSciVectorA':newSciVector,
                'ilgiFTVectorA': newFtVector
            }

            try:
                db.collection('Users').document(emailAdress).update(vectorData)
                return redirect(url_for('views.home'))
            except:
                return "<h1>Guncellenemedi</h1>"

        return render_template("recommends.html",sciDocsArray = sciDocsArray,ftDocsArray=ftDocsArray,currentuser = authFirebase.current_user,benzerliklerSci = en_benzer_besSci,benzerliklerFt = en_benzer_besFt)
    else:
        return redirect(url_for('auth.login'))



