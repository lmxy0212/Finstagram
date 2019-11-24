#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, send_file
import pymysql.cursors

import time
import hashlib
from functools import wraps
import os
IMAGES_DIR = os.path.join(os.getcwd(), "photos")

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
        return redirect(url_for('static', filename='home.html'))
    # return render_template("index.html")
    # data = open('templates/index.html').read()
    # return data
    return redirect(url_for('static', filename='index.html'))

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
    cursor = conn.cursor()
    cursor.execute(query, (photoID))
    photo = cursor.fetchone()

    # first last name of poster
    query = "SELECT firstName, lastName FROM Person WHERE username=%s"
    cursor = conn.cursor()
    cursor.execute(query, (session["username"]))
    name = cursor.fetchone()

    # being tagged
    query = "SELECT username, firstName, lastName " \
            "FROM Tagged NATURAL JOIN Person " \
            "WHERE photoID = %s AND tagstatus = 1"
    conn.cursor()
    cursor.execute(query, (photoID))
    tags = cursor.fetchall()

    # rating
    query = 'SELECT username, rating FROM Likes WHERE photoID = %s'
    cursor = conn.cursor()
    cursor.execute(query, (photoID))
    rating = cursor.fetchall()

    return render_template("view_further_info.html", photo=photo, name=name, tags=tags, ratings=rating)


@app.route("/photo/<image_name>", methods=["GET"])
def image(image_name):
    image_location = os.path.join(IMAGES_DIR, image_name)
    if os.path.isfile(image_location):
        return send_file(image_location, mimetype="image/jpg")


# ---------------------------- Post A Photo -----------------------------------------------
@app.route("/upload")
@login_required
def upload():
    return render_template("upload.html")


@app.route("/uploadPhoto", methods=["GET", "POST"])
@login_required
def uploadPhoto():
    if request.files:
        image_file = request.files.get("imageToUpload", "")
        image_name = image_file.filename
        filepath = os.path.join(IMAGES_DIR, image_name)
        print(filepath)
        image_file.save(filepath) 

        userName = session["username"]
        allFollowers = "0"
        caption = request.form.get('caption')
        display = request.form.get('display')

        #visible to all followers
        if display == "All Followers":
            allFollowers = "1"
            with conn.cursor() as cursor:
                query = "INSERT INTO Photo (postingDate, filePath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (time.strftime('%Y-%m-%d %H:%M:%S'), image_name, allFollowers, caption, userName))
                conn.commit()
                cursor.close()

        #visible to FriendGroup         
        else:
            res = display.split(",")
            groupName = res[0].split(":")[1]
            groupOwner = res[1].split(":")[1]
            query1 = "INSERT INTO Photo (postingDate, filePath, allFollowers, caption, photoPoster) VALUES (%s, %s, %s, %s, %s)"
            #insertion with SharedWith table (not sure???)
            query2 = "INSERT INTO SharedWith(groupOwner, groupName) VALUES (%s, %s)"
            with conn.cursor() as cursor:
                cursor.execute(query1, (time.strftime('%Y-%m-%d %H:%M:%S'), image_name, allFollowers, caption, userName))
                conn.commit()
                cursor.close()

        message = "Image has been successfully uploaded."
        return render_template("upload.html", message=message)

    else:
        message = "Failed to upload image."
        return render_template("upload.html", message=message) 
  
  
  

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
    return redirect(url_for('static', filename='home.html', username=session["username"]))


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
