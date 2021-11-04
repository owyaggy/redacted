from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #allow for session creation/maintenance
from flask import redirect
from os import urandom
import db
import sqlite3   #enable control of an sqlite database

app = Flask(__name__) #create Flask object
app.secret_key = urandom(32) #generates random key

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    data = [] #
    # check request method to use the right method for accessing inputs
    if (request.method == 'GET'):
        data = request.args
    else:
        data = request.form
    #print(data) #ImmutableMultiDict([('username', 'a'), ('password', 'a'), ('sub1', 'Login')])

    if ('sub2' in data): # sub2 is the logout button. user clicking it puts sub2 into data and ends the session
        session['login'] = False # end session
    if ('login' in session): # login is the login button
        if (session['login'] != False): # if user is not logged out, session['login'] is the user's username
            return redirect("/home") # landing page after login
    #print(session)

    if ('username' in data):
        if(request.method == 'GET'):
            name_input = request.args['username']
            pass_input = request.args['password']
        else:
            name_input = request.form['username']
            pass_input = request.form['password']

        error = "" # error message
        # a try catch block for anything unexpected happening
        try:
            error = db.get_login(name_input, pass_input) # check if the user exists in database
            if(error == ""):
                session["login"] = name_input # session username is stored
                print("hello") #check is the username was stores
                return redirect("/home") # render welcome page
        except Exception as e:
            error = e
        return render_template('login.html', error_message = error) # render login page with the correct error message
    return render_template('login.html') # otherwise render login page


@app.route("/home", methods=['GET', 'POST'])
def load_home():
    if(request.method == 'POST'):
        if(request.form['type'] == 'create'):
            db.create_story(request.form['title'], session["login"], request.form['content'])
        else:
            db.add_to_story(request.form["title"], session["login"], request.form["entry"])

    return render_template('home.html', name = session['login']) # render login page with an error message


@app.route("/create_account", methods=['GET', 'POST'])
def create_account_render():
    if('username' in request.form or 'username' in request.args): # check if input exists by checking if username input is in request dictionary
        name_input = "" #username input
        pass_input = "" #password input
        cpass_input = "" #confirm password
        error = "" # error message
        if(request.method == "GET"):
            name_input = request.args['username']
            pass_input = request.args['password']
            cpass_input = request.args['cpassword']
        else:
            name_input = request.form['username']
            pass_input = request.form['password']
            cpass_input = request.form['cpassword']
        # checks input for validity (it exists, passwords match, etc.)
        if(name_input == ""):
            error = "Username field cannot be blank!"
        elif(pass_input == ""):
            error = "Password field cannot be blank!"
        elif("\\n" in name_input):
            error = "Username cannot contain \\n!"
        elif(pass_input != cpass_input):
            error = "Password fields must match!"
        else:
            try:
                db.add_login(name_input, pass_input) # try to add u/p pair to db
                return redirect("/") # go back to main login page
            except sqlite3.IntegrityError: # error if the username is a duplicate
                error = "Username already exists!"
        # render the page after processing input
        return render_template('create_account.html', error_message = error)
    # render the page
    return render_template('create_account.html')


# stories got added is weird because of the number of times the scripts in db file is called
# should be fixed when everything is linked together and with better testing
@app.route("/add", methods=['GET', 'POST'])
def add_story_list():
    story_list = db.get_story_addable(session["login"]) # stories the user can add to
    #terminal testing prints
    #print("added to story")
    #print(get_story_last_entry(request.form["title"]))
    return render_template("add.html", collection = story_list)

# after submitting would go to the add page
@app.route("/add/<story>")
def add_a_story(story):
    #displays the contributor and the last entry of story
    last_entry = db.get_story_last_entry(story)
    return render_template('add_story.html', last_contributor = last_entry[0], last_entry = last_entry[1], title = story)

@app.route("/create", methods=['GET', 'POST'])
def create_story():
    return render_template('create.html')


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
    db.db.close()
