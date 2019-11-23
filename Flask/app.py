#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

import time
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
SALT = 'cs3083'


#Define a route to hello function
@app.route('/')
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("index.html")
  
#Make sure user is logged in for other actions
def login_required(func):
    @wraps(func)
    def dec(*args, **kwargs):
        if not "username" in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return dec


# --------------------------------- show visible photos ----------------------------------------------
@app.route("/photos", methods=["GET"])
@login_required
def photos():
    photoID = "1"
    cursor = conn.cursor()
    query = 'SELECT photoID, photoPoster FROM Photo ' \
           'WHERE photoID IN (SELECT photoID FROM SharedWith ' \
           'WHERE groupName IN (SELECT groupName FROM BelongTo ' \
           'WHERE member_username = %s OR owner_username = %s)) ORDER BY postingdate DESC'
    cursor.execute(query, (session['username'], session['username']))
    data = cursor.fetchall()
    return render_template("photos.html", photos=data)


# ---------------------------- View further photo info -----------------------------------------------
@app.route("/photos/<photoID>", methods=["GET"])
@login_required
def view_further_info(photoID):
    # photo
    query = "SELECT * FROM Photo WHERE photoID = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (photoID))
    photo = cursor.fetchone()
    # first last name
    query = "SELECT firstName, lastName FROM Person WHERE username=%s"
    with conn.cursor() as cursor:
        cursor.execute(query, (session["username"]))
    name = cursor.fetchone()
    # tagged
    # query = "SELECT username, firstName, lastName FROM Photo NATURAL JOIN TAGGED JOIN Person ON Person.photoPoster = Photo.photoID WHERE username=%s"
    # with conn.cursor() as cursor:
    #     cursor.execute(query, (session["username"]))
    # tags = cursor.fetchone()

    # query = "SELECT username FROM Tag WHERE photoID=%s AND acceptedTag=1"
    # with conn.cursor() as cursor:
    #     cursor.execute(query, (photoID))
    # tags = cursor.fetchall()

    return render_template("view_further_info.html", photo=photo, name=name)

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')


#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf - 8')).hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashed_password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf - 8')).hexdigest()
    firstName = request.form["fname"]
    lastName = request.form["lname"]
    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        try:
            with conn.cursor() as cursor:
                query = "INSERT INTO person (username, password, firstName, lastName) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, hashed_password, firstName, lastName))
        except pymysql.err.IntegrityError:
            error = "%s is already taken." % (username)
            return render_template('register.html', error=error)
        conn.commit()
        cursor.close()
        return redirect(url_for("login"))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=session["username"])


@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
