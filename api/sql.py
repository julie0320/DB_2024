from typing import Optional
import psycopg2
from psycopg2 import pool


class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  # 最小和最大連線數
        user='project_17',
        password='3dibeu',
        host='140.117.68.66',
        port='5432',
        dbname='project_17'
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input):
        if not isinstance(input, (tuple, list)):
            raise TypeError(f"Input should be a tuple or list, got: {type(input).__name__}")
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def execute(sql):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)


class Pizzaboy:
    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, eid, name FROM pizzaboy WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM pizzaboy"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO pizzaboy (name, account, password, phone, vehicle) VALUES (%s, %s, %s, %s,  %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['password'], input_data['phone'], input_data['vehicle']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_name(userid):
        sql = 'SELECT name FROM pizzaboy WHERE eid = %s'
        return DB.fetchone(sql, (userid,))
    

class Customer:
    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, mid, name FROM customer WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM customer"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO customer (name, account, password, address, phone) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['password'], input_data['address'], input_data['phone']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_name(userid):
        sql = 'SELECT name FROM customer WHERE mid = %s'
        return DB.fetchone(sql, (userid,))
    
    @staticmethod
    def get_mid(name):
        sql = 'SELECT mid FROM customer WHERE name = %s'
        return DB.fetchone(sql, (name,))


class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM cart, record 
                 WHERE cart.mid = %s::bigint 
                 AND cart.tno = record.tno::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))


class Pizza:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM pizza'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(pid):
        sql = 'SELECT * FROM pizza WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM pizza'
        return DB.fetchall(sql)

    @staticmethod
    def get_name(pid):
        sql = 'SELECT pname FROM pizza WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO pizza (pid, pname, price, pdesc) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['pname'], input_data['price'], input_data['pdesc']))

    @staticmethod
    def delete_product(pid):
        sql = 'DELETE FROM pizza WHERE pid = %s'
        DB.execute_input(sql, (pid,))

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE pizza SET pname = %s, price = %s,  pdesc = %s WHERE pid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['pdesc'], input_data['pid']))


class Record:
    @staticmethod
    def get_total_money(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]

    @staticmethod
    def check_product(pid, tno):
        sql = 'SELECT * FROM record WHERE pid = %s and tno = %s'
        return DB.fetchone(sql, (pid, tno))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM pizza WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO record (pid, tno, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['tno'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(tno):
        sql = 'SELECT * FROM record WHERE tno = %s'
        return DB.fetchall(sql, (tno,))

    @staticmethod
    def get_amount(tno, pid):
        sql = 'SELECT amount FROM record WHERE tno = %s and pid = %s'
        return DB.fetchone(sql, (tno, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE record SET amount = %s, total = %s WHERE pid = %s and tno = %s'
        DB.execute_input(sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['tno']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]


class Order_List:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO order_list (oid, mid, ordertime, price, tno) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'], input_data['format'], input_data['total'], input_data['tno']))

    @staticmethod
    def get_order():
        sql = '''
            SELECT o.oid, m.name, o.price, o.ordertime, COALESCE(o.pizzaboy, '')
            FROM order_list o
            NATURAL JOIN customer m
            ORDER BY o.ordertime DESC
        '''
        return DB.fetchall(sql)

    # 異動: 刪除訂單
    @staticmethod
    def delete_order(oid):
        sql = 'DELETE FROM order_list WHERE oid = %s'
        DB.execute_input(sql, (oid,))

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT o.oid, p.pname, r.saleprice, r.amount, o.pizzaboy
        FROM order_list o
        JOIN record r ON o.tno = r.tno -- 確保兩者都是 bigint 類型
        JOIN pizza p ON r.pid = p.pid
        '''
        return DB.fetchall(sql)
    
    # 異動: 檢查外送員
    @staticmethod
    def assign_delivery_pizzaboy(oid):
        sql = '''
            SELECT o.pizzaboy
            FROM order_list o
            WHERE o.oid = %s
        '''
        return DB.fetchall(sql, (oid,))
    
    # 異動: 新增接單外送員
    @staticmethod
    def update_pizzaboy(ename, oid):
        sql = 'UPDATE order_list SET pizzaboy = %s WHERE oid = %s'
        DB.execute_input(sql, (oid, ename))

    @staticmethod
    def get_total_money(oid):
        sql = '''
        SELECT r.saleprice
        FROM order_list o
        JOIN record r ON o.tno = r.tno -- 確保兩者都是 bigint 類型
        WHERE oid = %s
        '''
        return DB.fetchone(sql, (oid,))[0]




class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(saleprice), pname FROM pizza, record WHERE pizza.pid = record.pid GROUP BY pname'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), customer.mid, customer.name FROM order_list, customer WHERE order_list.mid = customer.mid GROUP BY customer.mid, customer.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        # sql = 'SELECT COUNT(*), customer.mid, customer.name FROM order_list, customer WHERE order_list.mid = customer.mid GROUP BY customer.mid, customer.name ORDER BY COUNT(*) DESC'
        sql = '''
        SELECT COUNT(*), customer.mid, customer.name FROM order_list, customer WHERE order_list.mid = customer.mid GROUP BY customer.mid, customer.name ORDER BY SUM(price) DESC

        '''
        return DB.fetchall(sql, ('user',))
    
    @staticmethod
    def best_selling_pizzas():
        # 這裡使用 SQL 查詢來獲取銷售總額前3名的商品
        query = """
        SELECT p.pname, SUM(r.amount * r.saleprice) AS total_sales
        FROM record r
        JOIN pizza p ON r.pid = p.pid
        GROUP BY p.pname
        ORDER BY total_sales DESC
        LIMIT 5;
        """

        return DB.fetchall(query, ())
