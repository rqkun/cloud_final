from flask import (
    Flask,
    request,
    render_template,
    url_for,
    session,
    redirect
)
import mysql.connector
import hashlib
import os
from werkzeug.utils import secure_filename

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
            cur.execute("SELECT count(productId) FROM kart WHERE userId = %s", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

@application.route('/')
def index():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('index.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 

@application.route('/product')
def product():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('product.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData) 


@application.route('/home')
def home():
    return redirect("/")

@application.route('/about')
def about():
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('about.html', loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems) 


@application.route("/add")
def admin():
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)

@application.route("/addItem", methods=["GET", "POST"])
def addItem():
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
            image.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
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
        return redirect(url_for('index'))

@application.route("/remove")
def remove():
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)

@application.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
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
    return redirect(url_for('index'))

@application.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = %s", (categoryId, ))
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@application.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@application.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('index'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = %s", (session['email'], ))
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

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

@application.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
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
            return redirect(url_for('index'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@application.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = %s', (productId, ))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)

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
                cur.execute("INSERT INTO kart (userId, productId) VALUES (%s, %s)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('index'))

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
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = %s", (userId, ))
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

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
            cur.execute("DELETE FROM kart WHERE userId = %s AND productId = %s", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('index'))

@application.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

def is_valid(email, password):
    con = mysql.connector.connect(host=CONN_HOST,user=CONN_USER,password=CONN_PASSWORD, database=CONN_DATABASE)
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

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

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)
