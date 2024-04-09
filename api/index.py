# Imports
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import json

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'  # Set the view for login
login_manager.init_app(app)  # Link login manager to the application

# Create database if not exists
def create_database():
    if not path.exists(DB_NAME):
        db.create_all()
        print("Database Created!!!")
    else:
        print("Database already exists!")

# User loader function for LoginManager
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Database models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(40))
    notes = db.relationship("Note", backref="user")

# Routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")
    return render_template("login.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email is already registered.", category="warning")
        elif len(email) < 4:
            flash("Email must be at least 3 characters long.", category="error")
        elif len(first_name) < 3:
            flash("First Name must be at least 2 characters long.", category="error")
        elif password1 != password2:
            flash("Passwords don't match", category="error")
        elif len(password1) < 3:
            flash("Password must be at least 3 characters", category="error")
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created", category="success")
            return redirect(url_for("home"))
    return render_template("sign_up.html", user=current_user)

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        note = request.form.get("note")
        if len(note) < 1:
            flash("Note is too short!", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("New note has been added.", category="success")
    return render_template("home.html", user=current_user)

@app.route("/delete-note", methods=["POST"])
def delete_note():
    note = json.loads(request.data)
    note_id = note["noteId"]
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


# Main block to run the app
if __name__ == "__main__":
    with app.app_context():  # Ensure running within application context
        create_database()
        app.run(debug=True)




# # from website import create_app

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy         # database connection
# from os import path 
# # user authentication
# from flask_login  import LoginManager          

# from flask import Blueprint, render_template, request, flash, redirect, url_for
# # from .models import User
# from werkzeug.security import generate_password_hash, check_password_hash
# # from . import db            # means from __init__.py import db
# from flask_login import login_user, login_required,  logout_user, current_user, UserMixin

# from sqlalchemy.sql import func
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# # from .models import Note
# import json

# db = SQLAlchemy()                               # define and initialize database
# DB_NAME = "database.db"


# app = Flask(__name__)                   # name of the file that ran "
# app.config["SECRET_KEY"] = "secret"     # encript or secure the cookies and sesson data related to the website
# app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'  # connect to SQLite database
# db.init_app(app)                          # initiate the database with the application

# def create_database():
#     if not path.exists(DB_NAME):
#         db.create_all()
#         print("Database Created!!!")
#     else:
#         print("Database already exists!")

# login_manager  = LoginManager()              # set up user authentication
# login_manager.login_view = 'login'      # redirect users to the login page
# login_manager.init_app(app)                # link login manager to the application

# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))       # get user by their ID







# @app.route("/login", methods=["GET","POST"])
# def login():
#     if request.method == "POST":
#         email =  request.form.get("email")
#         password = request.form.get("password")

#         user = User.query.filter_by(email=email).first()
#         if user:
#             if check_password_hash(user.password, password):
#                 flash("Logged in successfully!", category="success")
#                 login_user(user,  remember=True)
#                 return redirect(url_for("views.home"))
#             else:
#                 flash("Incorrect password, try again.", category="error")
#         else:
#             flash("Email does not exist.", category= "error")

#     return render_template("login.html", user=current_user)



# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("auth.login"))


# @app.route("/sign-up", methods=["GET","POST"])
# def sign_up():
#     if request.method == "POST":
#         email = request.form.get("email")
#         first_name = request.form.get("firstName")
#         password1 = request.form.get("password1")
#         password2 = request.form.get("password2")


#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash("This email is already registered.", category="warning")
#         elif len(email) < 4:
#             flash("Email must be at least 3 characters long.", category="Error")
#         elif len(first_name) < 3:
#             flash("First Name must be at least 2 characters long.", category="Error")
#         elif password1 != password2:
#             flash("Password dont match", category= "Error")
#         elif len(password1) < 3:
#             flash("Password must be at least 3 character", category="Error")
#         else:
#             new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(user,  remember=True)
#             flash("Account created", category="Success")        #add user to database
#             return redirect(url_for("views.home"))
        
#     return render_template("sign_up.html", user=current_user)



# class Note(db.Model):   # Creating a class for the database model of notes
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))     # The main content of the note
#     date = db.Column(db.DateTime(timezone=True), default=func.now())   # The date when the note was created
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))   # to connect users with their notes 
#     # How to associate different information with different user. if we have notes and we want to have notes that are being stored for each user, like each user has multipe notes.
#     #we need to setup a relationship between note-object and user-object. and this is done using a foreign key. So a foreign key essentially is a key on one of your database table
#     #that references id to another database column. So foreign key is a column in your database that always references a column of another database. so in this instance every single
#     # note, we want to store the ID of the user who created the note. 
#     # So Its(line 10) saying the type of colöumn is integer and by specifing a foreign key we must pass a valid id of an existing user to this column when we created a note object. This call 
#     #one to many rellationship that have one user and many notes(or parent child). In other words, we store a foreign key on each child-objects that referance the parent-object

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     first_name = db.Column(db.String(40)) 
#     notes = db.relationship("Note")




# # views = Blueprint("views", __name__)        # This(view) file is a blueprint of our application which means  
#                                             # it has bunch of roots, url defined in it. It just a way to  organize or saperate our app so we dont have to have all of our views defined in one file. we can have them defined in multiple file split up and nicely organize. 
# @app.route("/", methods=["GET", "POST"])           # with a decorater, defining root(slash '/') of the website
# @login_required
# def home():                 # we define home page as our root, so it will show whatever in home page
#     if request.method == "POST":  # If the method used to access
#         note = request.form.get("note")     # get data from HTML form by name="note"

#         if len(note) < 1:
#             flash("Note is too short!", category="error")
#         else:
#             new_note = Note(data=note, user_id=current_user.id)
#             db.session.add(new_note)       # Add this new note into database session
#             db.session.commit()             # Save all changes made in this session
#             flash("New note has been added.",  category="success")
#     return render_template("home.html", user=current_user)


# @app.route("/delet-note", methods=["POST"])      # /delete-note is the URL for deleting notes and using POST method
# def delete_note():
#     note = json.loads(request.data)         # Get id of the note that needs to be deleted
#     noteId = note["noteId"]
#     note = Note.query.get(noteId)          # Find the note with given Id
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()
            
            
#     return jsonify({})




# if __name__ == "__main__":
#     app.run(debug=True)           
     