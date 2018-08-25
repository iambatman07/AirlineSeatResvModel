from functools import wraps
import random
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import  sha256_crypt
app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='nandy' 
app.config['MYSQL_PASSWORD']='password'
app.config['MYSQL_DB']='airlines'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql = MySQL(app)


#Articles=Articles()
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Promo')
def promo():
    return render_template('promo.html')    

@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No articles Found'
        return render_template('articles.html', msg=msg)
    cur.close()

@app.route('/articles/<string:id>/')
def article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE id=%s",[id])
    article = cur.fetchone()

    return render_template('article.html',article=article)

class RegisterForm(Form):
    name = StringField('Name',[validators.length(min=1,max=30)])
    username  = StringField('Username',[validators.length(min=4,max=25)])
    email=StringField('Email',[validators.length(min=6,max=30)])
    age = StringField('Age', [validators.length(min=1, max=5)])
    phonenumber = StringField('Phonenumber', [validators.length(min=7, max=12)])
    address = StringField('Address', [validators.length(min=1, max=100)])
    password=PasswordField('Password',[validators.DataRequired(),
                                       validators.EqualTo('confirm',message='Passwords do not match')])
    confirm=PasswordField('confirm password')

@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if  request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        age=form.age.data
        phonenumber=form.phonenumber.data
        address=form.address.data
        password=sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO customer(custname,email,username,age,phonenum,address,password)VALUES(%s,%s,%s,%s,%s,%s, %s)",(name,email,username,age,phonenumber,address,password))
        mysql.connection.commit()
        cur.close()
        flash('Account Created Successfully.You can now Login.','success')

        return redirect(url_for('login'))

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password_candidate=request.form['password']

        cur = mysql.connection.cursor()
        result=cur.execute("SELECT * FROM customer WHERE username=%s",[username])

        if(result>0):
            data=cur.fetchone()
            password=data['password']
            custid=data['custid']
            
            if(sha256_crypt.verify(password_candidate,password)):
                #app.logger.info('password matched')
                session['logged_in']=True
                session['username']=username
                session['custid']=custid
                
                flash('logged in','success')
                return  redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error='Username not found'
            return render_template('login.html',error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash('Please Login','danger')
            return redirect(url_for('login'))

    return wrap


@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur=mysql.connection.cursor()
    usid=session.get('custid',None)
    
    result=cur.execute("SELECT * FROM bookings WHERE custid=%c",[usid])
    bookings=cur.fetchall()
    if result>0:
        return render_template('dashboard.html',bookings=bookings)
    else:
        msg='No bookings Found'
        return render_template('dashboard.html', msg=msg)
    cur.close()

@app.route('/flights')
def flights():
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT DISTINCT(flightnum),source,destination,timeofflight,bookingid FROM bookings GROUP BY flightnum")
    bookings=cur.fetchall()
    if result>0:
        return render_template('flights.html',bookings=bookings)
    else:
        msg='No Flights Found'
        return render_template('flights.html', msg=msg)
    cur.close()    

@app.route('/seatselect/<string:id>')
@is_logged_in
def seatselect(id):
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM bookings  WHERE bookingid=%s",[id])
    if(result>0):
        data=cur.fetchone()
        bookingid=data['bookingid']
        flightnum=data['flightnum']
        classs=data['class']    
        source=data['source']
        destination=data['destination']
        timeofflight=data['timeofflight']
        session['bookingid']=bookingid
        session['flightnum']=flightnum
        session['class']=classs
        session['source']=source[0:3]
        session['destination']=destination[0:3]
        session['timeofflight']=timeofflight
        if classs == 'E':   
            return  redirect(url_for('classe'))
        elif classs == 'B':      
            return  redirect(url_for('classb'))
        elif classs == 'F':  
            return  redirect(url_for('classf'))
    else:
        return redirect(url_for('dashboard'))
    cur.close()

@app.route('/classe')
def classe():
    return render_template('businessclass.html') 

@app.route('/classb')
def classb():
    return render_template('economyclass.html') 

@app.route('/classf')
def classf():
    return render_template('firstclass.html') 


@app.route('/addbooking/<string:id>',methods=['GET','POST'])
@is_logged_in
def addbooking(id):
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM bookings  WHERE bookingid=%s",[id])
    if(result>0):
        data=cur.fetchone()
        flightnum=data['flightnum']
        b = ['31555' , '41222' , '9799' , '87651' , '87654']
        u = random.randint(0,5)
        bookingid = flightnum + b[u]
        classs=data['class']    
        source=data['source']
        destination=data['destination']
        timeofflight=data['timeofflight']
        usid=session.get('custid',None)
        cur.execute("INSERT INTO bookings(bookingid,flightnum,seatsel,source,destination,class,timeofflight,custid) VALUES(%s,%s,%c,%s,%s,%s, %s, %c)",(bookingid,flightnum,0,source,destination,classs,timeofflight, usid))
        mysql.connection.commit()
        cur.close()
        flash('Booking Successful','success')
        return redirect(url_for('dashboard'))
    return render_template('home.html')
    


@app.route('/boardingpass')
@is_logged_in
def boardingpass():
    file = open("qrcode.txt","w")
    file.truncate()
    file.write("Custome Name:" + session['username'] +"source:" + session['source'] + "destination:" + session['destination'] + "Flight Number" + session['flightnum'] + "Class:" + session['class'] + "Date & Time of Flight:" + session['timeofflight'] + "Booking ID:" + session['bookingid'])
    file.close();
    return render_template('boardingpass.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("logout successfully",'success')
    return redirect(url_for('login'))

if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
