from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flaskdemodb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY']='secretkey'
app.config['SESSION_TYPE'] = 'filesystem'


db = SQLAlchemy(app)

migrate = Migrate(app, db)

class user_table(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(45), default='user')

class customer_table(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    FirstName = db.Column(db.String(45), nullable=False)
    MiddleName = db.Column(db.String(45), nullable=True)
    LastName = db.Column(db.String(45),nullable=False)
    status = db.Column(db.Integer, default=1)

@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('signin'))
    return render_template('/index.html', username=session['username'])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=generate_password_hash(request.form['password'])
        new_user=user_table(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))
    else:
        return render_template('/signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user = user_table.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username
            flash('You were successfully logged in','success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('/signin.html')

@app.route('/createcustomer', methods=['GET', 'POST'])
def createcustomer():
    if 'username' not in session:
        return redirect(url_for('signin'))
    if request.method=='POST':
        FirstName = request.form['FirstName']
        MiddleName = request.form['MiddleName']
        LastName = request.form['LastName']
        new_customer = customer_table(FirstName=FirstName, MiddleName= MiddleName, LastName=LastName)
        db.session.add(new_customer)
        db.session.commit()
        customers = customer_table.query.filter_by(status=1)
        return render_template('/create_customer.html', FirstName=FirstName, MiddleName= MiddleName, LastName=LastName, customers=customers, username=session['username'])
    else:
        customers = customer_table.query.filter_by(status=1)
        return render_template('/create_customer.html', customers=customers, username=session['username'])

@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    customers = customer_table.query.get_or_404(id)
    if request.method=='POST':
        FirstName = request.form['FirstName']
        MiddleName = request.form['MiddleName']
        LastName = request.form['LastName']

        customers.FirstName=FirstName
        customers.MiddleName=MiddleName
        customers.LastName=LastName

        db.session.add(customers)
        db.session.commit()

        return redirect(url_for('createcustomer'))
    return render_template('/edit.html', customers=customers)

@app.route('/<int:id>/delete/')
def delete(id):
    customers = customer_table.query.get_or_404(id)
    customers.status=0
    db.session.commit()
    return redirect(url_for('createcustomer'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect('signin')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)