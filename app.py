from flask import Flask,render_template,url_for,request,jsonify,redirect
from flask_cors import cross_origin
import requests
import pandas as pd
import numpy as np
import datetime
import pickle
import sklearn
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="templates")
model = pickle.load(open("df.pkl", 'rb'))

# Tells flask-sqlalchemy what database to connect to
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Enter a secret key
app.config["SECRET_KEY"] = "secretkey12"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()


login_manager = LoginManager()
login_manager.init_app(app)


# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)




@app.route("/",methods=['GET'])
@cross_origin()
def home():
	return render_template("index.html")


@app.route("/register" , methods=["GET", "POST"])
def register():
	
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                    password=request.form.get("password"))
        # Add the user to the database
        db.session.add(user)
        # Commit the changes made
        db.session.commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login" , methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by
    # filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        # Check if the password entered is the
        # same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return render_template("predict.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
        logout_user()
        return render_template("index.html")

@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method=="POST":
        return render_template('predict.html')


@app.route("/result", methods=['POST'])
def result():
    if request.method == 'POST':
        Gender = request.form['Gender']
        if Gender == "Male":
            Gender = 1
        else:
            Gender = 0

        Race=request.form['Race/ethnicity']
        if(Race=='Group A'):
            Race = 0
        elif(Race=="Group B"):
            Race = 1 
        elif(Race=="Group C"):
            Race = 2
        elif(Race=="Group D"):
            Race= 3
        else:
            Race = 4
        
        Parental_Level_of_Education = request.form['Parental_Level_of_Education']
        if Parental_Level_of_Education == "some high school":
            Parental_Level_of_Education = 5
        elif Parental_Level_of_Education =="high school":
            Parental_Level_of_Education =4
        elif Parental_Level_of_Education =="associate's degree":
            Parental_Level_of_Education = 3
        elif Parental_Level_of_Education == "master's degree":
            Parental_Level_of_Education = 2
        elif Parental_Level_of_Education == "some college":
            Parental_Level_of_Education = 1
        else :
            Parental_Level_of_Education = 0 


        Math_score = int(request.form['Math_Score'])

        Reading_score = int(request.form['Reading_score'])

        Writing_score = int(request.form['Writing_score'])


        Lunch = request.form['Lunch']
        if(Lunch=="standard"):
            Lunch = 1
        else:
            Lunch = 0
        
        test_preparation_course = request.form['test_preparation_course']
        if test_preparation_course == "None":
            test_preparation_course = 1
        else:
            test_preparation_course = 0


      
        prediction=model.predict(([[Gender,Race,Parental_Level_of_Education,Math_score,Reading_score,Writing_score,Lunch,test_preparation_course]]))
        print(prediction)
        prediction=np.round(prediction[0],2)
        return render_template('predict.html',Average=prediction)
    else:
        return render_template('predict.html')

if __name__=="__main__":
    app.run(debug=True)