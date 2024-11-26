import imp
from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import session
from link import *
from api.sql import *

api = Blueprint('api', __name__, template_folder='./templates')

login_manager = LoginManager(api)
login_manager.login_view = 'api.login'
login_manager.login_message = "請先登入"

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(userid):  
    
    print(f"Loading user with ID: {userid}")
    user = User()
    user.id = userid
    user_type = session.get('identity') 
    if user_type == 'customer':
        try:
            name = Customer.get_name(userid)[0]
            user.name = name
            user.role = 'customer'
        except:
            pass
    elif user_type == 'pizzaboy':
        try:
            name = Pizzaboy.get_name(userid)[0]
            user.name = name
            user.role = 'pizzaboy'
        except:
            pass
    else:
        return None

    return user


@api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        identity = request.form['identity']
        account = request.form['account']
        password = request.form['password']
        if(identity == 'pizzaboy'):
            print(account)
            data = Pizzaboy.get_member(account) 
            try:
                DB_password = data[0][1]
                user_id = data[0][2]
                #identity = data[0][3]

            except:
                flash('*沒有此帳號')
                return redirect(url_for('api.login'))

            if(DB_password == password ):
                user = User()
                user.id = user_id
                session['identity'] = 'pizzaboy'  # Store identity in session
                login_user(user)

                if( identity == 'pizzaboy'):
                    return redirect(url_for('manager.productManager'))
                else:
                    return redirect(url_for('bookstore.bookstore'))
            
            else:
                flash('*密碼錯誤，請再試一次')
                return redirect(url_for('api.login'))
        
        else:
            data = Customer.get_member(account) 
            try:
                DB_password = data[0][1]
                user_id = data[0][2]
                #identity = data[0][3]

            except:
                flash('*沒有此帳號')
                return redirect(url_for('api.login'))

            if(DB_password == password ):
                user = User()
                user.id = user_id
                session['identity'] = 'customer'
                login_user(user)

                if( identity == 'customer'):
                    return redirect(url_for('bookstore.bookstore'))
                else:
                    return redirect(url_for('manager.productManager'))
            
            else:
                flash('*密碼錯誤，請再試一次')
                return redirect(url_for('api.login'))

    
    return render_template('login.html')

@api.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_account = request.form['account']
        identity = request.form['identity']
        exist_account = Pizzaboy.get_all_account()
        account_list = []
        for i in exist_account:
            account_list.append(i[0])

        if(user_account in account_list):
            flash('Falied!')
            return redirect(url_for('api.register'))
        else:
            if(identity == 'pizzaboy'):
                input = { 
                    'name': request.form['username'], 
                    'account':user_account, 
                    'password':request.form['password'], 
                    'phone':request.form['phone'], 
                    'vehicle':request.form['vehicle']
                }
                Pizzaboy.create_member(input)
                return redirect(url_for('api.login'))
            else:
                input = { 
                    'name': request.form['username'], 
                    'account':user_account, 
                    'password':request.form['password'], 
                    'phone':request.form['phone'], 
                    'address':request.form['address']
                }
                Customer.create_member(input)
                return redirect(url_for('api.login'))

    return render_template('register.html')

@api.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))