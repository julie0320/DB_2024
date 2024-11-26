from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/orderTracker', methods=['GET', 'POST'])
@login_required
def orderTracker():
    order_data = []
    order_detail = []
    # 訂單被刪除
    if 'delete' in request.values:
        oid = request.values.get('delete')
        data = Record.delete_check(oid)
        print(oid)
        
        if(data != None):
            flash('failed')
        else:
            Order_List.delete_order(oid)
            return redirect(url_for('manager.orderTracker'))
        
    # 新增接單外送員
    if 'pizzaboy_add' in request.values:
        oid = request.values.get('pizzaboy_add')
        pizzaboy = request.values.get('ename')
        print(oid)
        print(pizzaboy)
        
        if pizzaboy is None or pizzaboy.strip() == '':
            flash('failed')
        else:
            Order_List.update_pizzaboy(oid, pizzaboy)
            return redirect(url_for('manager.orderTracker'))

    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        # order_data = []
        for i in order_row:
            status = "已接單" if i[4] else "未接單"
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3],
                '接單外送員': i[4],
                '訂單狀態': status
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        # order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3],
                '接單外送員': j[4]
            }
            order_detail.append(orderdetail)

    return render_template('orderTracker.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    # if request.method == 'GET':
    #     if(current_user.role == 'user'):
    #         flash('No permission')
    #         return redirect(url_for('index'))
        
    if 'delete' in request.values:
        pid = request.values.get('delete')
        data = Record.delete_check(pid)
        
        if(data != None):
            flash('failed')
        else:
            data = Pizza.get_product(pid)
            Pizza.delete_product(pid)
    
    elif 'edit' in request.values:
        pid = request.values.get('edit')
        return redirect(url_for('manager.edit', pid=pid))
    
    pizza_data = pizza()
    return render_template('productManager.html', pizza_data = pizza_data, user=current_user.name)

def pizza():
    book_row = Pizza.get_all_product()
    book_data = []
    for i in book_row:
        book = {
            '商品編號': i[0],
            '商品名稱': i[1],
            '商品售價': i[2],
        }
        book_data.append(book)
    return book_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            pid = en + number
            data = Pizza.get_product(pid)

        pname = request.values.get('pname')
        price = request.values.get('price')
        file = request.files.get('file')
        pdesc = request.values.get('description')
        print(file.filename)
        file.save(f'static/img/{pname}.png')
        file_path = f'static/img/{file.filename}'  # 異動:圖片路徑從這裡存
        # 檢查是否正確獲取到所有欄位的數據
        if pname is None or price is None or file is None or pdesc is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.productManager'))

        # 檢查欄位的長度
        if len(pname) < 1 or len(price) < 1:
            flash('商品名稱或價格不可為空。')
            return redirect(url_for('manager.productManager'))


        if (len(pname) < 1 or len(price) < 1):
            return redirect(url_for('manager.productManager'))
        

        # 上傳圖片在這裡
        Pizza.add_product(
            {'pid' : pid,
             'pname' : pname,
             'price' : price,
             'pdesc':pdesc,
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Pizza.update_product(
            {
            'pname' : request.values.get('pname'),
            'price' : request.values.get('price'),
            'pdesc' : request.values.get('description'),
            'pid' : request.values.get('pid')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    pid = request.args['pid']
    data = Pizza.get_product(pid)
    pname = data[1]
    price = data[2]
    description = data[3]

    product = {
        '商品編號': pid,
        '商品名稱': pname,
        '單價': price,
        '商品敘述': description
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3]
            }
            order_data.append(order)
            
        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)