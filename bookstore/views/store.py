import re
import os
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random, string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Pizzaboy, Customer, Order_List, Pizza, Record, Cart

store = Blueprint('bookstore', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def bookstore():
    from math import ceil
    # 預設每頁顯示9筆商品
    items_per_page = 9
    flag = 0
    page = int(request.args.get('page', 1))  # 默認頁數為1
    search = request.args.get('keyword', None)  # 搜索關鍵字
    start = (page - 1) * items_per_page
    end = page * items_per_page

    # 查詢商品數量
    if search:
        cursor.execute('SELECT * FROM Pizza WHERE PNAME LIKE %s', ('%' + search + '%',))
    else:
        cursor.execute('SELECT * FROM Pizza')
    
    book_row = cursor.fetchall()
    book_data = []
    total = len(book_row)
    
    # 篩選商品並添加到book_data
    for i in book_row:
        image_url = f'./img/{i[1]}.png'
        book = {
            '商品編號': i[0],
            '商品名稱': i[1],
            '商品價格': i[2],
            'image_url': image_url
        }
        book_data.append(book)

    # 計算總頁數
    count = ceil(total / items_per_page)
    
    # 分頁邏輯：從起始頁範圍選取資料
    final_data = book_data[start:end]
    
    # 檢查是否達到最後一頁
    if len(final_data) < end - start:
        flag = 1  # 如果剩餘商品少於一頁，設定flag標記

    if 'pid' in request.args:
        pid = request.args['pid']
        data = Pizza.get_product(pid)
        
        pname = data[1]
        price = data[2]
        description = data[3]
        
        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '單價': price,
            '商品敘述': description,
        }

        return render_template('product.html', data = product, user=current_user.name)

    return render_template('bookstore.html', 
                           book_data=final_data, 
                           user=current_user.name, 
                           keyword=search, 
                           page=page, 
                           flag=flag, 
                           count=count)
    
# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def cart():
    # # 以防管理者誤闖
    # if request.method == 'GET':
    #     if (current_user.role == 'manager'):
    #         flash('No permission')
    #         return redirect(url_for('manager.home'))

    # 回傳有 pid 代表要 加商品
    if request.method == 'POST':
        if "pid" in request.form:
            data = Cart.get_cart(current_user.id)

            if data is None:  # 假如購物車裡面沒有他的資料
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                Cart.add_cart(current_user.id, time)  # 幫他加一台購物車
                data = Cart.get_cart(current_user.id)

            tno = data[2]  # 取得交易編號
            pid = request.form.get('pid')  # 使用者想要購買的東西，使用 `request.form.get()` 來避免 KeyError
            if not pid:
                flash('Product ID is missing.')
                return redirect(url_for('bookstore.cart'))  # 返回購物車頁面並顯示錯誤信息

            # 檢查購物車裡面有沒有商品
            product = Record.check_product(pid, tno)
            # 取得商品價錢
            price = Pizza.get_product(pid)[2]

            # 如果購物車裡面沒有的話，把它加一個進去
            if product is None:
                Record.add_product({'pid': pid, 'tno': tno, 'saleprice': price, 'total': price})
            else:
                # 如果購物車裡面有的話，就多加一個進去
                amount = Record.get_amount(tno, pid)
                total = (amount + 1) * int(price)
                Record.update_product({'amount': amount + 1, 'tno': tno, 'pid': pid, 'total': total})

        elif "delete" in request.form:
            pid = request.form.get('delete')
            tno = Cart.get_cart(current_user.id)[2]

            Customer.delete_product(tno, pid)
            product_data = only_cart()

        elif "user_edit" in request.form:
            change_order()
            return redirect(url_for('bookstore.bookstore'))

        elif "buy" in request.form:
            change_order()
            return redirect(url_for('bookstore.order'))

        elif "order" in request.form:
            tno = Cart.get_cart(current_user.id)[2]
            total = Record.get_total_money(tno)
            Cart.clear_cart(current_user.id)

            time = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            format = 'yyyy/mm/dd hh24:mi:ss'
            Order_List.add_order({'mid': current_user.id, 'ordertime': time, 'total': total, 'format': format, 'tno': tno})

            return render_template('complete.html', user=current_user.name)

    product_data = only_cart()
    try:
        tno = Cart.get_cart(current_user.id)[2]
        total = Record.get_total_money(tno)
    except:
        tno = ""
        total=""

    if product_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=product_data, user=current_user.name, total=total)


@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pname = Pizza.get_name(i[1])
        product = {
            '商品編號': i[1],
            '商品名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        product_data.append(product)
    
    total = int(Record.get_total(tno))  # 將 Decimal 轉換為 INT


    return render_template('order.html', data=product_data, total=total, user=current_user.name)

@store.route('/orderlist')
def orderlist():
    if "oid" in request.args :
        pass
    
    user_id = current_user.id

    data = Customer.get_order(user_id)
    orderlist = []

    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[3],
            '訂單時間': i[2]
        }
        orderlist.append(temp)
    
    orderdetail_row = Order_List.get_orderdetail()
    orderdetail = []

    for j in orderdetail_row:
        temp = {
            '訂單編號': j[0],
            '商品名稱': j[1],
            '商品單價': j[2],
            '訂購數量': j[3]
        }
        orderdetail.append(temp)
    try:
        # tno = Cart.get_cart(j[0])
        total = Order_List.get_total_money(j[0])
    except:
        tno = ""
        total=""

    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name, total=total)

def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2] # 使用者有購物車了，購物車的交易編號是什麼
    product_row = Record.get_record(data[2])

    for i in product_row:
        
        # i[0]：交易編號 / i[1]：商品編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_product({
                'amount':request.form[i[1]],
                'pid':i[1],
                'tno':tno,
                'total':int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0


def only_cart():
    count = Cart.check(current_user.id)

    if count is None:
        return 0

    data = Cart.get_cart(current_user.id)
    tno = data[2]
    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pid = i[1]
        pname = Pizza.get_name(i[1])
        price = i[3]
        amount = i[2]

        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        product_data.append(product)

    return product_data