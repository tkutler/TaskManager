from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt 
app = Flask(__name__)
bcrypt= Bcrypt(app)
import re
app.secret_key = "I am a secret key" 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
db ="exam"


@app.route('/')
def index():
    return render_template("index.html")
@app.route('/register', methods= ["POST"])
def register():
    mysql = connectToMySQL(db)
        
    if len(request.form['first']) < 1:
    	flash("Please enter a valid first name")
    if len(request.form['last']) <1:
        flash("Please enter valid last name") 
    if len(request.form["password"]) < 1:
        flash("password lenth must be more than 0 ")
    if len(request.form["passwordconfirm"]) < 1:
        flash("password lenth must be more than 0 ")
    if request.form['password'] != request.form['passwordconfirm']:
        flash ("passsword does not match")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if '_flashes' in session.keys():
        return redirect("/")
    if not '_flashes' in session.keys(): 
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        
        query = "INSERT INTO users (first, last, email, password) VALUES (%(first)s, %(last)s, %(email)s, %(pw)s); "
        data = {
            "first": request.form["first"],
            "last": request.form["last"],
            "email": request.form["email"],
            "pw": pw_hash
        }
        userid = mysql.query_db(query,data)
        session['userid'] = userid
        mysql = connectToMySQL(db)
        query = "SELECT first FROM users WHERE idusers =" + str(userid)+";"
        username = mysql.query_db(query,data)
        session["username"] = username[0]['first']
        return redirect ("/dashboard")
@app.route("/login", methods = ["POST"]) 
def login():
    mysql = connectToMySQL(db)
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        "email" : request.form['userlogin']
    }
    users = mysql.query_db(query, data)
    
    
    if users: 
        if bcrypt.check_password_hash(users[0]['password'], request.form['passwordlogin']):
            session['userid'] = users[0]['idusers']
            session['username'] = users[0]['first']
            session['useremail'] = users[0]['email']
            print("password found")
            return redirect ('/dashboard')
        else: 
            flash("not successful")
            print("password not found")
            return redirect ("/")
    else: 
        flash("not successful") 
        print("email not found")  
        return redirect ("/")     

@app.route("/dashboard")
def dashboard():
    mysql = connectToMySQL(db)
    query = "select * from users join jobs on idusers = poster"
    dash = mysql.query_db(query)
    return render_template("login.html", dash = dash) 
@app.route('/logout')
def logout():
    session.clear()
    print('you are logged out')
    return redirect ('/') 
@app.route ('/jobs/new')
def newjob():
    mysql = connectToMySQL(db)
    query = "select * from users"
    users = mysql.query_db(query)
    return render_template ('newjob.html', users = users)
@app.route ('/add', methods = ["POST"])
def addjob():
    mysql = connectToMySQL(db) 
    if len(request.form['title']) < 3:
    	flash("Please enter a valid title") 
    if len(request.form['location']) < 3:
        flash("Please enter a valid location")
    if len(request.form['descr']) < 3:
        flash("Please enter a valid description")
    if '_flashes' in session.keys():
        return redirect ("/jobs/new")
    if not '_flashes' in session.keys():
        query = "INSERT INTO jobs (job,location,description,poster) VALUES (%(job)s, %(location)s, %(description)s, %(poster)s);"
        data = {
            "job": request.form['title'],
            "location": request.form['location'],
            "description": request.form ['descr'],
            "poster": request.form['poster']
        }
        newjob = mysql.query_db(query,data)  
        return redirect ('/dashboard') 
@app.route ('/jobs/<id>')
def showjob(id):
    mysql = connectToMySQL(db) 
    query ="select * from users join jobs on idusers = poster where idjobs="+ id + ";"
    jobinfo = mysql.query_db(query) 
    return render_template ('jobinfo.html', jobinfo = jobinfo) 
@app.route ('/jobs/edit/<id>')
def edit(id): 
    mysql = connectToMySQL(db)
    query = "select * from jobs where idjobs = "+ id + ";"
    job = mysql.query_db(query)
    return render_template ('editjob.html', job= job[0]) 
@app.route ('/edit/<id>', methods= ["POST"]) 
def makeedit(id):
    print ("in route")
    mysql = connectToMySQL(db)
    if len(request.form['tit']) < 3:
    	flash("Please enter a valid title")
    if len(request.form['loca']) < 3:
        flash("Please enter a valid location")
    if len(request.form['descript']) < 3:
        flash("Please enter a valid description")
    if '_flashes' in session.keys():
        return redirect ('/jobs/edit/' + id ) 
    if not '_flashes' in session.keys(): 
        query = "UPDATE exam.jobs SET job= %(job)s, location= %(location)s, description =%(description)s WHERE idjobs= "+ id + ";"
        data = {
            "job": request.form["tit"],
            "location": request.form["loca"],
            "description": request.form['descript']
        }
        mysql.query_db(query,data) 
        return redirect ('/dashboard')
    
    
@app.route ('/remove/<id>')
def remove (id): 
   mysql = connectToMySQL(db) 
   query = "DELETE FROM jobs WHERE idjobs ="+ id + ";"
   mysql.query_db(query) 
   return redirect ('/dashboard')









    

















if __name__ == "__main__":
    app.run(debug=True)