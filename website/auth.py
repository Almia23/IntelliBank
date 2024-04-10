from flask import Blueprint, render_template, redirect, flash, url_for, request
from .models import User, Employee, Savings, Currents, Transactions
from . import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import random

auth=Blueprint('auth', __name__)

@auth.route('/')
def about():
    logout_user()
    return render_template("about.html", user=current_user)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if(check_password_hash(user.password,password)):
                logout_user()
                login_user(user)
                flash('Logged in successfully', category='success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email doesnt exist, please sign up', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/emplogin', methods=['GET','POST'])
def emplogin():
    if request.method == 'POST':
        email= request.form.get('email')
        password = request.form.get('password')
        user = Employee.query.filter_by(email=email).first()
        if not user:
            flash("Email doesn't exist, please contact manager", category='error')
        elif user.id==101:
            if(check_password_hash(user.password,password)):
                flash('Manager logged in', category='success')
                logout_user()
                login_user(user)
                return redirect(url_for('auth.mngrprofile'))
            else:
                flash('Incorrect password, try again', category='error')
        elif user:
            if(check_password_hash(user.password,password)):
                logout_user()
                login_user(user)
                flash('Logged in successfully', category='success')
                return redirect(url_for('auth.empprofile'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email doesnt exist, please contact manager', category='error')
            
    return render_template("emplogin.html", user=current_user)

@auth.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        empnums = Employee.query.count()
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Phone already exists', category='error')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(first_name)<2:
            flash('First name must be greater than 1 character', category='error')
        elif len(last_name)<2:
            flash('Last name must be greater than 1 character', category='error')
        elif len(phone)<10:
            flash('Phone must be atleast 10 characters', category='error')
        elif password1!=password2:
            flash('Passwords dont match', category='error')
        elif len(password1)<7:
            flash('Password must be greater than 7 characters', category='error')
        else:
            new_user = User(first_name=first_name, last_name=last_name, phone=phone, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'), managedBy=random.randint(102,100+empnums))
            db.session.add(new_user)
            db.session.commit()
            flash('User added', category='success')
            user = User.query.filter_by(email=email).first()
            new_acc = Currents(userid=user.id)
            db.session.add(new_acc)
            db.session.commit()
            flash('Account created', category='success')
            login_user(new_user, remember=True)
            return redirect('/profile')
    return render_template("signup.html", user=current_user)








###############################



@auth.route('/empsignup', methods=['POST', 'GET'])
def empsign_up():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        
        user = Employee.query.filter_by(phone=phone).first()
        if user:
            flash('Phone number already exists', category='error')
        user = Employee.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(first_name)<2:
            flash('First name must be greater than 1 character', category='error')
        elif len(last_name)<2:
            flash('Last name must be greater than 1 character', category='error')
        elif len(phone)<10:
            flash('Phone must be atleast 10 characters', category='error')
        elif password1!=password2:
            flash('Passwords dont match', category='error')
        elif len(password1)<7:
            flash('Password must be greater than 7 characters', category='error')
        else:
            new_user = Employee(first_name=first_name, last_name=last_name, phone=phone, email=email, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('User added', category='success')
    return render_template("empsignup.html", user=current_user)



############################

@auth.route('/profile')
@login_required
def profile():
    user = current_user
    current=Currents.query.filter_by(userid=user.id).first()
    saving=Savings.query.filter_by(userid=user.id).first()
    return render_template("profile.html", user=current_user, current=current, saving=saving)

@auth.route('/transaction', methods=['GET','POST'])
@login_required
def transaction():
    if request.method == 'POST':
        option = request.form.get('choice')
        acc = request.form.get('account')
        password = request.form.get('password')
        amount = int(request.form.get('amount'))

        user = current_user
        if acc=='current':
            account=Currents.query.filter_by(userid=user.id).first()
        else:
            account=Savings.query.filter_by(userid=user.id).first()
                
        if not check_password_hash(user.password,password):
            flash('Incorrect password', category='error')
        elif not account:
            flash('Account doesnt exist', category='error')
        elif option=='withdraw':
            if account.balance<amount:
                flash('Not enough balance', category='error')
            else:
                try:
                    account.balance=account.balance-amount
                    db.session.commit()
                    new_transaction = Transactions(from_ac=account.acnum, to_ac=account.acnum, amount=-amount)
                    db.session.add(new_transaction)
                    db.session.commit()
                    flash('Amount withdrawn', category='success')
                except:
                    flash('Error in withdrawing', category='error')
                return redirect('/profile')
            return render_template("transaction.html", user=current_user)
        elif option=='deposit':
            try:
                account.balance=account.balance+amount
                db.session.commit()
                new_transaction = Transactions(from_ac=account.acnum, to_ac=account.acnum, amount=amount)
                db.session.add(new_transaction)
                db.session.commit()
                flash('Amount deposited', category='success')
            except:
                flash('Error in depositing', category='error')
            return redirect('/profile')
    return render_template("transaction.html", user=current_user)

@auth.route('/transfer', methods=['POST','GET'])
@login_required
def transfer():
    if request.method == 'POST':
        first_name = request.form.get('firstName') #receiver details
        email = request.form.get('email')
        password = request.form.get('password') #sender password
        amount = int(request.form.get('amount'))
        acc = request.form.get('account')

        sender = current_user
        if acc=='current':
            account=Currents.query.filter_by(userid=sender.id).first()
        else:
            account=Savings.query.filter_by(userid=sender.id).first()
        receiver = User.query.filter_by(email=email).first()
        receiveracc = Currents.query.filter_by(userid=receiver.id).first()
        
        if not receiver:
            flash('User doesnt exist', category='error')
        elif receiver.first_name!=first_name:
            flash('Incorrect name', category='error')
        elif not check_password_hash(sender.password,password):
            flash('Incorrect password', category='error')
        elif not account:
            flash('Account doesnt exist', category='error')
        elif account.balance<amount:
            flash('Not enough balance', category='error')
        else:
            try:
                account.balance=account.balance-amount
                receiveracc.balance=receiveracc.balance+amount
                db.session.commit()
                new_transaction = Transactions(from_ac=account.acnum, to_ac=receiveracc.acnum, amount=-amount)
                db.session.add(new_transaction)
                db.session.commit()
                flash('Amount transfered', category='success')
            except:
                flash('Error in transferring', category='error')
            return redirect('/profile')
    return render_template("transfer.html", user=current_user)

@auth.route('/transactLog')
@login_required
def transactLog():
    user=current_user
    current=Currents.query.filter_by(userid=user.id).first()
    saving=Currents.query.filter_by(userid=user.id).first()
    transacts=Transactions.query.filter_by(from_ac=current.acnum).union(Transactions.query.filter_by(to_ac=current.acnum))
    return render_template("transactLog.html", user=current_user, transacts=transacts)

@auth.route('/savings', methods=['POST','GET'])
@login_required
def savings():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        accountType = request.form.get('accountType')
        amount = int(request.form.get('amount'))
        
        user = User.query.filter_by(email=email).first()
        saving = Savings.query.filter_by(userid=user.id).first()
        current = Currents.query.filter_by(userid=user.id).first()
        if saving:
            flash('Savings account already present', category='error')
            return redirect('/profile')
        if not user:
            flash('Incorrect email', category='error')
        elif not check_password_hash(user.password,password):
            flash('Incorrect password', category='error')
        elif accountType not in ['1','2','3']:
            flash('Incorrect category', category='error')
        elif current.balance<amount:
            flash('Not enough balance', category='error')
        else:
            try:
                current.balance=current.balance-amount
                useridforac=user.id
                newsavings = Savings(acnum=current.acnum, userid=useridforac, balance=amount, accountType=accountType)
                db.session.add(newsavings)
                db.session.commit()
                flash('Savings account created', category='success')
                saving = Savings.query.filter_by(userid=user.id).first()
                new_transaction = Transactions(from_ac=current.acnum, to_ac=saving.acnum, amount=-amount)
                db.session.add(new_transaction)
                db.session.commit()
            except:
                flash('Error in creating savings account', category='error')
            return redirect('/profile')
    return render_template("savings.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.about'))

@auth.route('/empprofile')
@login_required
def empprofile():
    return render_template("empprofile.html", user=current_user)

@auth.route('/empAllUsers')
@login_required
def empAllUsers():
    user=current_user
    users=User.query.filter_by(managedBy=user.id)
    return render_template("empAllUsers.html", user=current_user, users=users)

@auth.route('/empAllTrans')
@login_required
def empAllTrans():
    user=current_user
    useracc=User.query.filter_by(managedBy=user.id)
    transacts=Transactions.query.filter_by(from_ac=current.acnum).union(Transactions.query.filter_by(to_ac=current.acnum))
    
    current=Currents.query.filter_by(userid=user.id)
    saving=Currents.query.filter_by(userid=user.id).first()
    transacts=Transactions.query.filter_by(from_ac=current.acnum).union(Transactions.query.filter_by(to_ac=current.acnum))
    
    
    return render_template("empAllTrans.html", user=current_user, transacts=transacts)
    
@auth.route('/mngrprofile')
@login_required
def mngrprofile():
    return render_template("mngrprofile.html", user=current_user)

@auth.route('/mngrAllUsers')
@login_required
def mngrAllUsers():
    users=User.query.all()
    return render_template("mngrAllUsers.html", user=current_user, users=users)

@auth.route('/mngrAllTrans')
@login_required
def mngrAllTrans():
    user=current_user
    transacts=Transactions.query.all()
    return render_template("mngrAllTrans.html", user=current_user, transacts=transacts)
    
    

@auth.route('/editUser', methods=['GET','POST'])
def editUser():
    user = current_user
    
    if request.method == 'POST':
        user.first_name = request.form['fname']
        user.last_name = request.form['lname']
        user.phone = request.form['phone']
        user.email = request.form['email']
        try:
            db.session.commit()
            flash('Updated', category='success')
            return redirect(url_for('auth.profile'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.editUser'))
    return render_template('editUser.html', user=current_user)

@auth.route('/empEditProf', methods=['GET','POST'])
def empEditProf():
    user = current_user
    
    if request.method == 'POST':
        user.first_name = request.form['fname']
        user.last_name = request.form['lname']
        user.phone = request.form['phone']
        user.email = request.form['email']
        try:
            db.session.commit()
            flash('Updated', category='success')
            return redirect(url_for('auth.empprofile'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.empEditProf'))
    return render_template('empEditProf.html', user=current_user)