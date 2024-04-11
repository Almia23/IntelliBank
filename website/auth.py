from flask import Blueprint, render_template, redirect, flash, url_for, request
from .models import User, Employee, Savings, Currents, Transactions
from . import db
from datetime import datetime
from sqlalchemy.sql import func, text, extract
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
            flash('Employee added', category='success')
    return render_template("empsignup.html", user=current_user)



############################


@auth.route('/profile')
@login_required
def profile():
    user = current_user
    current=Currents.query.filter_by(userid=user.id).first()
    saving=Savings.query.filter_by(userid=user.id).first()
    date=datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    if saving:
        days = date.day-saving.lastupdated.day
        if days>=1:
            if saving.accountType==1:
                rate=0.01
            elif saving.accountType==2:
                rate=0.025
            elif saving.accountType==3:
                rate=0.04
            for i in range (0,days):
                saving.balance += saving.balance*rate
            db.session.commit()
    return render_template("profile.html", user=current_user, current=current, saving=saving)

@auth.route('/transaction', methods=['GET','POST'])
@login_required
def transaction():
    if request.method == 'POST':
        option = request.form.get('choice')
        acc = request.form.get('account')
        password = request.form.get('password')
        amount = int(request.form.get('amount'))
        date=datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        user = current_user
        if acc=='current':
            account=Currents.query.filter_by(userid=user.id).first()
        else:
            account=Savings.query.filter_by(userid=user.id).first()
            if account:
                days = date.day-account.lastupdated.day
                if days>=1:
                    if account.accountType==1:
                        rate=0.01
                    elif account.accountType==2:
                        rate=0.025
                    elif account.accountType==3:
                        rate=0.04
                    for i in range (0,days):
                        account.balance += account.balance*rate
                db.session.commit()        
        if not check_password_hash(user.password,password):
            flash('Incorrect password', category='error')
        elif not account:
            flash('Account doesnt exist', category='error')
        elif option=='withdraw':
            if account.balance<amount:
                flash('Not enough balance', category='error')
            elif amount>1000 and acc=='saving':
                flash('Only upto 1000 can be withdrawn from savings account', category='error')
            else:
                try:
                    account.balance=account.balance-amount
                    db.session.commit()
                    new_transaction = Transactions(from_ac=account.acnum,from_type=acc, to_ac=account.acnum,to_type=acc, amount=-amount)
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
                new_transaction = Transactions(from_ac=account.acnum,from_type=acc, to_ac=account.acnum,to_type=acc, amount=amount)
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
        date=datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        sender = current_user
        if acc=='current':
            account=Currents.query.filter_by(userid=sender.id).first()
        else:
            account=Savings.query.filter_by(userid=sender.id).first()
            if account:
                days = date.day-account.lastupdated.day
                if days<1:
                    if account.accountType==1:
                        rate=0.01
                    elif account.accountType==2:
                        rate=0.025
                    elif account.accountType==3:
                        rate=0.04
                    for i in range (0,days):
                        account.balance += account.balance*rate
                account.lastupdated=func.now()
                db.session.commit()
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
        elif amount>1000 and acc=='saving':
            flash('Only upto 1000 can be transferred from savings account', category='error')
        else:
            try:
                account.balance=account.balance-amount
                receiveracc.balance=receiveracc.balance+amount
                db.session.commit()
                new_transaction = Transactions(from_ac=account.acnum,from_type=acc, to_ac=receiveracc.acnum,to_type="current", amount=-amount)
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
                new_transaction = Transactions(from_ac=current.acnum, from_type='current', to_ac=saving.acnum,to_type='saving', amount=-amount)
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
    #db.session.query(db.func.sum(Services.price)).filter(Services.dateAdd.between(start, end))
    #this for interest
    #select * from transactions where from_ac in(select acnum from currents where userid in(select id from user where managedBy=current_user.id))
    results = db.session.query(User.id).filter_by(managedBy=current_user.id).all()
    results2 = [list(row) for row in results]
    newl = [i for i2 in results2 for i in i2]

    subquery2 = db.session.query(Currents.acnum).filter(Currents.userid.in_(newl)).all()
    resultsq2 = [list(row) for row in subquery2]
    newl2 = [i for i2 in resultsq2 for i in i2]
    
    transacts=db.session.query(Transactions).filter(Transactions.from_ac.in_(newl2))
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

@auth.route('/mngrAllEmployees')
@login_required
def mngrAllEmployees():
    users=Employee.query.all()
    return render_template("mngrAllEmployees.html", user=current_user, users=users)


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
        
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.editUser'))
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
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.empEditProf'))
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

@auth.route('/mngrEditProf', methods=['GET','POST'])
def mngrEditProf():
    user = current_user
    
    if request.method == 'POST':
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.mngrEditProf'))
        user.first_name = request.form['fname']
        user.last_name = request.form['lname']
        user.phone = request.form['phone']
        user.email = request.form['email']
        try:
            db.session.commit()
            flash('Updated', category='success')
            return redirect(url_for('auth.mngrprofile'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.mngrEditProf'))
    return render_template('mngrEditProf.html', user=current_user)



@auth.route('/empEditUser/<int:id>', methods=['GET','POST'])
def empEditUser(id):
    user=current_user
    cust=User.query.get_or_404(id)
    if request.method == 'POST':
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.empAllUsers'))
        cust.first_name = request.form['fname']
        cust.last_name = request.form['lname']
        cust.phone = request.form['phone']
        cust.email = request.form['email']
        try:
            db.session.commit()
            flash('User updated', category='success')
            return redirect(url_for('auth.empAllUsers'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.empAllUsers'))
    else:
        return render_template('empEditUser.html', user=user, cust=cust)
    
@auth.route('/empDeleteUser/<int:id>')
def empDeleteUser(id):
    cust= User.query.get_or_404(id)
    try:
        db.session.delete(cust)
        db.session.commit()
        flash('User deleted', category='success')
        return redirect(url_for('auth.empAllUsers'))
    except:
        flash('Error in deleting', category='error')
        return redirect(url_for('auth.empAllUsers'))
    
@auth.route('/mngrEditUser/<int:id>', methods=['GET','POST'])
def mngrEditUser(id):
    user=current_user
    cust=User.query.get_or_404(id)
    if request.method == 'POST':
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.mngrAllUsers'))
        cust.first_name = request.form['fname']
        cust.last_name = request.form['lname']
        cust.phone = request.form['phone']
        cust.email = request.form['email']
        try:
            db.session.commit()
            flash('User updated', category='success')
            return redirect(url_for('auth.mngrAllUsers'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.mngrAllUsers'))
    else:
        return render_template('mngrEditUser.html', user=user, cust=cust)
    
@auth.route('/mngrDeleteUser/<int:id>')
def mngrDeleteUser(id):
    cust= User.query.get_or_404(id)
    try:
        db.session.delete(cust)
        db.session.commit()
        flash('User deleted', category='success')
        return redirect(url_for('auth.mngrAllUsers'))
    except:
        flash('Error in deleting', category='error')
        return redirect(url_for('auth.mngrAllUsers'))
    
@auth.route('/mngrEditEmp/<int:id>', methods=['GET','POST'])
def mngrEditEmp(id):
    user=current_user
    cust=Employee.query.get_or_404(id)
    if request.method == 'POST':
        password=request.form['password']
        if not (check_password_hash(user.password,password)):
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.mngrAllEmployees'))
        cust.first_name = request.form['fname']
        cust.last_name = request.form['lname']
        cust.phone = request.form['phone']
        cust.email = request.form['email']
        cust.salary = request.form['salary']
        try:
            db.session.commit()
            flash('Employee updated', category='success')
            return redirect(url_for('auth.mngrAllEmployees'))
        except:
            flash('Error in updating', category='error')
            return redirect(url_for('auth.mngrAllEmployees'))
    else:
        return render_template('mngrEditEmp.html', user=user, cust=cust)
    
@auth.route('/mngrDeleteEmp/<int:id>')
def mngrDeleteEmp(id):
    cust= Employee.query.get_or_404(id)
    try:
        db.session.delete(cust)
        db.session.commit()
        flash('Employee deleted', category='success')
        return redirect(url_for('auth.mngrAllEmployees'))
    except:
        flash('Error in deleting', category='error')
        return redirect(url_for('auth.mngrAllEmployees'))