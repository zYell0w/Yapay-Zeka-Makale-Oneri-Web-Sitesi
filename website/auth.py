from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from firebase_admin import credentials
from firebase_admin import firestore
from .functions import *

#Firebase Auth Kurulumu
auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if(authFirebase.current_user):
            return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        ilgi_Alani = request.form.get('ilgiAlani')
        ilgi_AlaniArray = ilgi_Alani.split(",")

        
        ilgiSciVector, ilgiFTVector = vectorGettingilgi(ilgi_AlaniArray)
        ilgiSciVectorA = ilgiSciVector.tolist()
        ilgiFTVectorA = ilgiFTVector.tolist()

        userData = {
        'email' : email,
        'first_name' : first_name,
        'ilgi_Alani' : ilgi_AlaniArray,
        'ilgiSciVectorA':ilgiSciVectorA,
        'ilgiFTVectorA':ilgiFTVectorA
        }

        try:
            user = authFirebase.create_user_with_email_and_password(email,password)
            authFirebase.current_user = user
            db.collection('Users').document(f"{email}").set(userData)
            return redirect(url_for('views.home'))
        except:
            return render_template("sign_up.html")
        
    return render_template("sign_up.html")
        
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        

        try:
            user = authFirebase.sign_in_with_email_and_password(email,password)
            authFirebase.current_user = user

            
            return redirect(url_for('views.home'))
            
        except:
            return redirect(url_for('auth.login'))   

    return render_template("login.html")

@auth.route('/logout')
def logout():
    try:
        authFirebase.current_user = None
    except:
        redirect(url_for('auth.login'))
    return redirect(url_for('auth.login'))


