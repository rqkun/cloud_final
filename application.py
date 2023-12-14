from flask import Flask, request, render_template, url_for, session, redirect
from flask_paginate import Pagination, get_page_args
import mysql.connector
import hashlib
import os
from werkzeug.utils import secure_filename
import time
import uuid

application = Flask(__name__,static_url_path='/static')

application.static_folder = 'static'

# A secret key that will be used for securely signing the session cookie and can be used for any other security related needs by extensions or your application. 
# It should be a long random bytes or str. For example, copy the output of this to your config:
application.secret_key = '!1@2#3$4%5^6&7*8(9)0aswdfzxcvbnhgtynm'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
CONN_HOST = "mysql8003.site4now.net"
CONN_USER = "aa2631_shopdb"
CONN_PASSWORD = "12345asd"
CONN_DATABASE = "db_aa2631_shopdb"

# The config is actually a subclass of a dictionary and can be modified just like any dictionary
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def getLoginDetails():
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = %s", (session['email'], ))
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM cart WHERE userId = %s", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

# Main page
# DONE
@application.route('/')
def index():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products LIMIT 4')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    #itemData = parse(itemData)
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 

@application.route('/admin')
def administrator():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    if is_admin(email) == False:
        return redirect(url_for('index'))
<<<<<<< Updated upstream
    else: return render_template('admin.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems) 
=======
    else: 
        return render_template('admin.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems) 
>>>>>>> Stashed changes

# Search
# DONE
@application.route('/search', methods=['POST'])
def search():
    loggedIn, firstName, noOfItems = getLoginDetails()
    itemName = request.form['searchBox']
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE LOWER(products.name) LIKE %s',('%'+itemName.lower()+'%',))
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    total = len(itemData)
    #itemData = parse(itemData)

    page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
    pagination_data = itemData[offset:offset+per_page]
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')

    return render_template('searchResult.html', itemData=pagination_data, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData = categoryData)

# View product
# DONE
# With paging
@application.route('/product')
def product():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    total = len(itemData)
    #itemData = parse(itemData)

    page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
    per_page = 16
    pagination_data = itemData[offset:offset+per_page]
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')

    return render_template('product.html', itemData=pagination_data, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 

@application.route('/home')
def home():
    return redirect("/")

# Dunno
@application.route('/about')
def about():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    #itemData = parse(itemData)
    return render_template('about.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData = categoryData) 

# Add item
# DONE
@application.route("/add")
def addProduct():
    email = session['email']
    if is_admin(email) == True:
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT categoryId, name FROM categories")
            categories = cur.fetchall()
        conn.close()
        return render_template('add.html', categories=categories)
    return redirect(url_for('index'))

@application.route("/addItem", methods=["GET", "POST"])
def addItem():
    email = session['email']
    if is_admin(email) == True:
        if request.method == "POST":
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            stock = int(request.form['stock'])
            categoryId = int(request.form['category'])

            #Uploading image procedure
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                basedir = os.path.abspath(os.path.dirname(__file__))
                image.save(os.path.join(basedir, application.config['UPLOAD_FOLDER'], filename))
            imagename = filename
            with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (%s, %s, %s, %s, %s, %s)''', (name, price, description, imagename, stock, categoryId))
                    conn.commit()
                    msg="added successfully"
                except:
                    msg="error occured"
                    conn.rollback()
            conn.close()
            print(msg)
            return redirect(url_for('administrator'))
    return redirect(url_for('index'))

# Remove item
@application.route("/remove")
def remove():
<<<<<<< Updated upstream
=======
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == True:
        loggedIn, firstName, noOfItems = getLoginDetails()
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        total = len(itemData)
        #itemData = parse(itemData)

        page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
        per_page=16
        pagination_data = itemData[offset:offset+per_page]
        pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')

        return render_template('remove.html', itemData=pagination_data, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 
<<<<<<< Updated upstream
    return redirect(url_for('index'))

@application.route("/productDescriptionForRemove")
def productDescriptionForRemove():
=======
    return redirect(url_for('index')) 

@application.route("/productDescriptionForRemove")
def productDescriptionForRemove():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == True:
        loggedIn, firstName, noOfItems = getLoginDetails()
        productId = request.args.get('removeProductId')
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = %s', (productId, ))
            productData = cur.fetchone()
        conn.close()
        return render_template("productDescriptionForRemove.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)
    return redirect(url_for('index'))

@application.route("/removeItem")
def removeItem():
<<<<<<< Updated upstream
=======
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == True:
        productId = request.args.get('removedProductId')
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            try:
                cur = conn.cursor()
                cur.execute('DELETE FROM products WHERE productID = %s', (productId, ))
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('remove'))
    return redirect(url_for('index'))

# Update item
@application.route("/updateStock")
def updateStock():
<<<<<<< Updated upstream
=======
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == True:
        loggedIn, firstName, noOfItems = getLoginDetails()
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        total = len(itemData)

        page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
        per_page=16
        pagination_data = itemData[offset:offset+per_page]
        pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')
        return render_template('updateStock.html', itemData=pagination_data, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 
    return redirect(url_for('index'))

@application.route("/productDescriptionForUpdate")
def productDescriptionForUpdate():
<<<<<<< Updated upstream
=======
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == True:
        loggedIn, firstName, noOfItems = getLoginDetails()
        productId = request.args.get('updatedProductId')
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = %s', (productId, ))
            productData = cur.fetchone()
        conn.close()
        return render_template("productDescriptionForUpdate.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)
    return redirect(url_for('index'))

@application.route("/updateProduct", methods=['POST', 'GET'])
def updateProduct():
<<<<<<< Updated upstream
=======
    if 'email' not in session:
        return redirect(url_for('loginForm'))
>>>>>>> Stashed changes
    email = session['email']
    if is_admin(email) == False:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            productId = request.args.get('updatedProductId')
            additional = int(request.form.get('quantity'))
            with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute('SELECT stock FROM products WHERE productId = %s', (productId, ))
                    currentStock = cur.fetchone()[0]
                    cur.execute('UPDATE products SET stock = %s WHERE productId = %s', (currentStock + additional, productId))
                    conn.commit()
                    msg = "Update successsfully"
                    print(msg)
                except:
                    conn.rollback()
                    msg = "Error occured"
            conn.close()
        return redirect(url_for('updateStock'))

# Display item by category
# DONE
@application.route("/displayCategory")
def displayCategory():
    loggedIn, firstName, noOfItems = getLoginDetails()
    categoryId = request.args.get("categoryId")
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = %s", (categoryId, ))
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    total = len(itemData)
    conn.close()
    categoryName = itemData[0][4]

    page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
    pagination_data = itemData[offset:offset+per_page]
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')
    #data = parse(data)
    return render_template('displayCategory.html', itemData=pagination_data, categoryData=categoryData, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

# View profile
# DONE
@application.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = %s", (session['email'], ))
        profileData = cur.fetchone()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    conn.close()
    return render_template("profileHome.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,categoryData=categoryData)

# Update profile
# DONE
@application.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = %s", (session['email'], ))
        profileData = cur.fetchone()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,categoryData=categoryData)

@application.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1'] 
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
                try:
                    cur = conn.cursor()
                    cur.execute('UPDATE users SET firstName = %s, lastName = %s, address1 = %s, address2 = %s, zipcode = %s, city = %s, state = %s, country = %s, phone = %s WHERE email = %s', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    conn.commit()
                    msg = "Saved Successfully"
                except:
                    conn.rollback()
                    msg = "Error occured"
        conn.close()
        return redirect(url_for('editProfile'))

# Change password
# DONE - redirect to profile page if needed
@application.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = %s", (session['email'], ))
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = %s WHERE userId = %s", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

# Login
# Admin: admin@admin.com   -   12345asd
# DONE
@application.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error='')

@application.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            if is_admin(email):
                return redirect(url_for('administrator'))
            else: 
                return redirect(url_for('index'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

# View product detail
# DONE
@application.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = %s', (productId, ))
        productData = cur.fetchone()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems,categoryData=categoryData)

# Add item to cart
# DONE
@application.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = %s", (session['email'], ))
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO cart (userId, productId) VALUES (%s, %s)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('product'))

# View your cart
# DONE
@application.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, cart WHERE products.productId = cart.productId AND cart.userId = %s", (userId, ))
        products = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,categoryData=categoryData)

# Remove item from cart
# DONE
@application.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart WHERE userId = %s AND productId = %s", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

# Checkout
# DONE
@application.route("/checkoutForm")
def checkoutForm():
    # Lấy id user /
    # Lấy id product /
    # Nếu quantity product = 0 -> báo lỗi /
    # Else:
    #   Hiện form checkout: Tên. SDT. Address. 
    #   Tạo Order theo user id, orderId = str(uuid.uuid4())
    #   Tạo Order detail thei orderId và productId
    #   Trừ quantity của product
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]

        cur.execute("SELECT productId FROM cart WHERE userId = %s", (userId, ))
        cart = cur.fetchall()
        productIdList =[]
        totalPrice = 0
        for row in cart:
            cur.execute("SELECT stock, price, name FROM products WHERE productId = %s", (row[0], ))
            product = cur.fetchone()
            if product[0] > 0:
                productIdList.append(row)
                totalPrice += product[1]
            else:
                redirect(url_for('cart'))
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    conn.close()
    return render_template("checkout.html", totalPrice=totalPrice,categoryData=categoryData)

@application.route("/checkout", methods = ['GET', 'POST'])
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == 'POST':
        email = session['email']
        name = request.form['receiverName']
        address = request.form['receiverAddress']
        phone = request.form['phone']
        orderId = str(uuid.uuid4())
        print(len(orderId))
        
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
            userId = cur.fetchone()[0]
            try:
                # Create order
                cur.execute('INSERT INTO orders (orderId, userId, receiverName, shippingAddress, phone) VALUES (%s, %s, %s, %s, %s)', (orderId, userId, name, address, phone))
                conn.commit()

                # Create order detail
                cur.execute("SELECT productId FROM cart WHERE userId = %s", (userId, ))
                cart = cur.fetchall()
                for row in cart:
                    cur.execute('INSERT INTO orderdetail (orderId, productId) VALUES (%s, %s)', (orderId, row[0]))
                    conn.commit()

                # Remove user cart
                cur.execute('DELETE FROM cart WHERE userId = %s', (userId, ))
                conn.commit()

                msg = "Checkout Successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for("product"))

# My orders
# DONE
@application.route("/account/orders")
def myOrders():
    # Lấy toàn bộ orders theo userId
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0]
        cur.execute("SELECT orderId, receiverName, shippingAddress, phone FROM orders WHERE userId = %s", (userId, ))
        orders = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    total = len(orders)

    page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
    pagination_data = orders[offset:offset+per_page]
    pagination = Pagination(page=page,per_page=per_page,total=total,css_framework='bootstrap4')

    return render_template("myOrders.html", orders = pagination_data, page=page, per_page=per_page, pagination=pagination, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)

# Order detail
# DONE
@application.route("/orderDetail")
def orderDetail():
    # Nhận orderId
    # Lấy toàn bộ details theo orderId
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    orderId = request.args.get('orderId')
    #email = session['email']
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        """ cur.execute("SELECT userId FROM users WHERE email = %s", (email, ))
        userId = cur.fetchone()[0] """
        cur.execute("SELECT orders.orderId, products.name, products.price, products.image, orders.receiverName, orders.shippingAddress, orders.phone \
                    FROM orders INNER JOIN orderDetail ON orders.orderId = orderdetail.orderId \
                    INNER JOIN products ON orderdetail.productId = products.productId \
                    WHERE orderDetail.orderId = %s \
                    AND products.productId = orderDetail.productId", (orderId, ))
        products = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("orderDetail.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems,categoryData=categoryData)

# Log out 
# DONE
@application.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

# Check account
# DONE
def is_valid(email, password):
    con = mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE)
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

# Check admin
def is_admin(email):
    con = mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE)
    cur = con.cursor()
    cur.execute('SELECT userId, email FROM users WHERE email = %s', (email, ))
    userId = cur.fetchone()[0]
    if userId == 1:
        return True
    return False

# Create new account
# DONE
@application.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            try:
                cur = conn.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))

                conn.commit()

                msg = "Registered Successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return render_template("login.html", error=msg)

@application.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)
