# coding=utf-8

import os
from flask import Flask, render_template, request, Response, jsonify, send_file, url_for, redirect, session
import database as db
import gridfs
import secrets
import datetime
from models.user import User
from models.product import Product
from models.cart import Cart
from models.order import Order
from models.restaurant import Restaurant
from models.recipe import Recipe

db = db.dbConnection()
app = Flask(__name__)
app.secret_key = '218366d271c2f7cf88fcd8b24917c23b'
app.config['UPLOAD_FOLDER'] = 'static/img/products'

# INDEX

@app.route('/')
def home():
    return render_template('index.html', restaurant=is_restaurant())


# USER 

def is_restaurant():
    return session.get('restaurant', False)

@app.route('/account')
def account():
    if 'username' in session:
        user = session['username']
        return render_template('account.html', user=user, restaurant=is_restaurant())
    return render_template('account.html', restaurant=is_restaurant())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = db['users']
        restaurants = db['restaurants']
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({"email": email, "password": password})
        restaurant = restaurants.find_one({"email": email, "password": password})
        if user:
            session['username'] = user['username']
            session['email'] = user['email']
            session['restaurant'] = False
            return redirect(url_for('account'))
        elif restaurant:
            session['username'] = restaurant['name']
            session['email'] = restaurant['email']
            session['restaurant'] = True
            return redirect(url_for('account'))
        return render_template('login.html', error='El correo o la contraseña son incorrectos', restaurant=is_restaurant())
    else:
        return render_template('login.html', restaurant=is_restaurant())

@app.route('/register-user', methods=['GET','POST'])
def register_user():
    if request.method == 'POST':
        users = db['users']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if username and email and password:
            user = User(username, email, password)
            if users.find_one({'email': email}):
                return render_template('register-user.html', error='El correo ya está en uso', restaurant=is_restaurant())
            users.insert_one(user.toBDCollection())
            session['username'] = username
            session['email'] = email
            session['restaurant'] = False
            return redirect(url_for('account'))
        else:
            return render_template('register-user.html', error='Por favor llene todos los campos', restaurant=is_restaurant())
    else:
        return render_template('register-user.html', restaurant=is_restaurant())

@app.route('/register-restaurant', methods=['GET','POST'])
def register_restaurant():
    if request.method == 'POST':
        email = request.form['email']
        restaurant = set_restaurant(request)
        restaurants = db['restaurants']
        users = db['users']
        username = request.form['username']
        if restaurants.find_one({'email': email}) or users.find_one({'email': email}):
            return render_template('register-restaurant.html', error='El correo ya está en uso', restaurant=is_restaurant())
        restaurants.insert_one(restaurant.toBDCollection())
        session['username'] = username
        session['email'] = email
        session['restaurant'] = True
        return redirect(url_for('account'))
    else:
        return render_template('register-restaurant.html', restaurant=is_restaurant())

@app.route('/logout') 
def logout():
    if 'username' in session:
        session.pop('username',None)
        session.pop('email',None)
        session.pop('restaurant',None)
        return redirect('/')

@app.route('/update-account', methods=['GET', 'POST'])
def update_account():
    if session['restaurant']:
        restaurants = db['restaurants']
        restaurant = restaurants.find_one({'email': session['email']})
        if request.method == 'POST':
            email = request.form['email']
            new_restaurant = set_restaurant(request, id_restaurant=restaurant['_id'])
            users = db['users']
            username = request.form['username']
            if restaurants.find_one({'email': email, '_id': {"$ne": restaurant['_id']}}) or users.find_one({'email': email}):
                return render_template('register-restaurant.html', error='El correo ya está en uso', restaurant=is_restaurant())
            session['username'] = username
            session['email'] = email
            session['restaurant'] = True
            restaurants.update_one({'_id': restaurant['_id']}, {'$set': new_restaurant.updateDBCollection()})
            return redirect(url_for('account'))
        return render_template('update-restaurant.html', restaurant=is_restaurant(), rest=restaurant)
    else:
        users = db['users']
        user = users.find_one({'email': session['email']})
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            new_user = User(username, email, password)
            restaurants = db['restaurants']
            if restaurants.find_one({'email': email}) or users.find_one({'email': email, '_id': {"$ne": user['_id']}}):
                return render_template('update-user.html', error='El correo ya está en uso', restaurant=is_restaurant(), user=user)
            users.update_one({'email': session['email']}, {'$set': new_user.toBDCollection()})
            session['username'] = username
            session['email'] = email
            session['restaurant'] = False
            return redirect(url_for('account'))
        return render_template('update-user.html', restaurant=is_restaurant(), user=user)


# RESTAURANT

@app.route('/delete-restaurant')
def delete_restaurant():
    restaurants = db['restaurants']
    restaurants.delete_one({'email': session['email']})
    session.pop('username',None)
    session.pop('email',None)
    session.pop('restaurant',None)
    return redirect('/')

@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants():
    restaurants = db['restaurants']
    categories = restaurants.distinct('category')
    if request.method == 'POST':
        restaurant = request.form['search']
        category = request.form['category']
        if category == 'all':
            restaurants = restaurants.find({'name': {'$regex': restaurant, '$options': 'i'}})
        else:
            restaurants = restaurants.find({'name': {'$regex': restaurant, '$options': 'i'}, 'category': category})
        return render_template('restaurants.html', restaurants=restaurants, restaurant=is_restaurant(), categories=categories)
    return render_template('restaurants.html', restaurants=restaurants.find({}), restaurant=is_restaurant(), categories=categories)

# PRODUCT

@app.route('/products', methods=["GET", "POST"])
def products():
    error = request.args.get('error')
    restaurants = db['restaurants']
    id_restaurant = request.args.get('id_restaurant')
    if id_restaurant:
        restaurant = restaurants.find_one({'_id': int(id_restaurant)})
    else:
        restaurant = restaurants.find_one({'email': session['email']})
        
    products_list = restaurant.get('products', [])
    products = list(db['products'].find({'_id': {'$in': products_list}}))
    if request.method == 'POST':
        name = request.form['search']
        products = list(db['products'].find({'_id': {'$in': products_list}, 'name': {'$regex': name, '$options': 'i'}}))
    if is_restaurant():
        return render_template('products-admin.html', restaurant=is_restaurant(), rest=restaurant, products=products)
    return render_template('products.html', restaurant=is_restaurant(), rest=restaurant, products=products, error=error)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        products = db['products']
        product = set_product(request)
        products.insert_one(product.toDBCollection())
        restaurants = db['restaurants']
        restaurant = restaurants.find_one({'email': session['email']})
        products = restaurant.get('products', [])
        products.append(product.id)
        restaurants.update_one({'email': session['email']}, {'$set': {'products': products}})
        return redirect(url_for('products'))
    return render_template('add-product.html', restaurant=is_restaurant())        

@app.route('/update-product/<int:id_product>', methods=['GET', 'POST'])
def update_product(id_product):
    products = db['products']
    product = products.find_one({'_id': id_product})
    if request.method == 'POST':
        product = set_product(request, id_product = id_product)
        products.update_one({'_id': id_product}, {'$set': product.updateDBCollection()})
        return redirect(url_for('products'))
    return render_template('update-product.html', restaurant=is_restaurant(), product=product)

@app.route('/delete-product/<int:id_product>')
def delete_product(id_product):
    products = db['products']
    product = products.find_one({'_id': id_product})
    if product:
        products.delete_one({'_id': id_product})
        restaurants = db['restaurants']
        restaurant = restaurants.find_one({'email': session['email']})
        products = restaurant.get('products', [])
        products.remove(id_product)
        restaurants.update_one({'email': session['email']}, {'$set': {'products': products}})
        return redirect(url_for('products', error='Producto eliminado correctamente :^)'))
    return redirect(url_for('products', error='El producto no existe'))


# CART

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    error = request.args.get('error')
    if 'username' in session:
        users = db['users']
        user = users.find_one({"email": session['email']})
        if 'cart' in user:
            carts = db['carts']
            cart = carts.find_one({"_id": user['cart']})
            if request.method == 'POST':
                quantities = request.form.getlist('quantity')
                table = request.form['table']
                for i in range(len(cart['products'])):
                    cart['products'][i]['quantity'] = quantities[i]
                    cart['products'][i]['unit_total'] = int(cart['products'][i]['price']) * int(quantities[i])
                    cart['total'] = sum([int(product['unit_total']) for product in cart['products']])
                    carts.update_one({'_id': user['cart']}, {'$set': cart})
                    return redirect(url_for('make_order', id_cart=user['cart'], table=table))
            return render_template('cart.html', cart=cart,  restaurant=is_restaurant(), user=user, error=error)
        else:
            return render_template('cart.html',  restaurant=is_restaurant(), user=user, error='Su carrito de compras está vacío ;(')
    return render_template('cart.html',  restaurant=is_restaurant(), error="Inicie sesión para ver su carrito de compras, o cree una cuenta si no tiene una :^)")

@app.route('/add-to-cart/<int:id_product>', methods=["GET", "POST"])
def add_to_cart(id_product):
    products = db['products']
    product = products.find_one({"_id": id_product})
    users = db['users']
    user = users.find_one({"email": session['email']})
    carts = db['carts']
    product['quantity'] = 1
    product['unit_total'] = product['price']
    restaurants = db['restaurants']
    restaurant = restaurants.find_one({'products': id_product})
    if 'cart' in user:
        id_cart = user['cart']
        cart = carts.find_one({"_id": id_cart})
        if cart['restaurant']['_id'] != restaurant['_id']:
            return redirect(url_for('products', id_restaurant=restaurant['_id'], error='No puedes agregar productos de distintos restaurantes a tu carrito de compras :^('))
        index = next((i for i, product in enumerate(cart['products']) if product['_id'] == id_product), None)
        if index is not None:
            product_in_cart = cart['products'][index]
            cart['products'][index]['quantity'] += 1
            cart['products'][index]['unit_total'] = product_in_cart['quantity'] * int(product_in_cart['price'])
        else:
            cart['products'].append(product)
        cart_total = sum(int(product['unit_total']) for product in cart['products'])
        carts.update_one({"_id": id_cart}, {"$set": {"products": cart['products'], "total": cart_total}})
    else:
        id_cart = get_id(carts)
        cart = Cart(id_cart, restaurant, [product], product['price'])
        carts.insert_one(cart.toDBCollection())
        users.update_one({"email": session['email']}, {"$set": {"cart": id_cart}})
    return redirect(url_for('products', error='Producto añadido al carrito :^)', id_restaurant=restaurant['_id']))

@app.route('/remove-from-cart/<int:id_product>')
def remove_from_cart(id_product):
    products = db['products']
    product = products.find_one({"_id": id_product})
    users = db['users']
    user = users.find_one({"email": session['email']})
    carts = db['carts']
    id_cart = user['cart']
    cart = carts.find_one({"_id": id_cart})
    index = next((i for i, product in enumerate(cart['products']) if product['_id'] == id_product), None)
    cart['products'].pop(index)
    cart_total = sum(int(product['unit_total']) for product in cart['products'])
    if cart_total == 0:
        carts.delete_one({"_id": id_cart})
        users.update_one({"email": session['email']}, {"$unset": {"cart": ""}})
    carts.update_one({"_id": id_cart}, {"$set": {"products": cart['products'], "total": cart_total}})
    return redirect(url_for('cart', error='Producto eliminado del carrito ;('))


# ORDER

@app.route('/order')
def order():
    if request.method == 'POST':
        id_order = request.form['order']
        orders = db['orders']
        order = orders.find_one({'_id': id_order})
        if not order:
            error = 'No se encontró ninguna orden, verifique el id ;('
        return render_template('order.html', order=order, restaurant=is_restaurant(), error=error)
    return render_template('order.html', restaurant=is_restaurant())

@app.route('/orders')
def orders():
    error = request.args.get('error')
    if 'username' in session:
        users = db['users']
        user = users.find_one({"email": session['email']})
        if is_restaurant():
            orders = db['orders']
            orders = list(orders.find())
            orders.reverse()
            for order in orders:
                order['client'] = users.find_one({"orders": order['_id']})
            return render_template('orders-admin.html', restaurant=is_restaurant(), user=user, orders=orders)
        if 'orders' not in user:
            return render_template('orders.html', restaurant=is_restaurant(), user=user, error='No tiene ninguna orden :(')
        orders = db['orders']
        restaurants = db['restaurants']
        orders_list = []
        for id_order in user['orders']:
            order = orders.find_one({"_id": id_order})
            order['restaurant'] = restaurants.find_one({"orders": order['_id']})
            orders_list.append(order)
        orders_list.reverse()
        return render_template('orders.html', orders=orders_list, restaurant=is_restaurant(), user=user, error=error)
    return render_template('orders.html', restaurant=is_restaurant(), error="Inicie sesión para ver su historial de órdenes, o cree una cuenta si no tiene una :^)")

@app.route('/make-order/<int:id_cart>', methods=["GET", "POST"])
def make_order(id_cart):
    table = request.args.get('table')
    carts = db['carts']
    restaurants = db['restaurants']
    cart = carts.find_one({"_id": id_cart})
    users = db['users']
    user = users.find_one({"email": session['email']})
    orders = db['orders']
    id_order = get_id(orders)
    date = datetime.datetime.now()
    order = Order(id_order, table, cart['products'], cart['total'], date)
    orders.insert_one(order.toDBCollection())
    users.update_one({"email": session['email']}, {"$unset": {"cart": ""}})
    carts.delete_one({"_id": id_cart})
    restaurant = restaurants.find_one({'_id': cart['restaurant']['_id']})
    user_orders = user.get('orders', []).append(id_order)
    users.update_one({"email": session['email']}, {"$set": {"orders": [id_order]}})
    restaurant_orders = restaurant.get('orders', []).append(id_order)
    restaurants.update_one({"_id": restaurant['_id']}, {"$set": {"orders": [id_order]}})
    return redirect(url_for('orders', error='Orden realizada correctamente :^)'))

@app.route('/delivered-order/<int:id_order>')
def delivered_order(id_order):
    orders = db['orders']
    order = orders.find_one({"_id": id_order})
    if order['delivered']:
        orders.update_one({"_id": id_order}, {"$set": {"delivered": False}})
    else:
        orders.update_one({"_id": id_order}, {"$set": {"delivered": True}})
    return redirect(url_for('orders'))

@app.route('/cancel-order/<int:id_order>')
def cancel_order(id_order):
    orders = db['orders']
    orders.update_one({"_id": id_order}, {"$set": {"status": "canceled"}})
    return redirect(url_for('orders', error='Orden cancelada correctamente :^)'))

# UTILS

def get_id(collection):
    if collection.count_documents({}) == 0:
        return 0
    return collection.find().sort('_id', -1).limit(1)[0]['_id'] + 1

def set_restaurant(request, *args, **kwargs):
    restaurants = db['restaurants']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    description = request.form['description']
    address = request.form['address']
    category = request.form['category']

    if 'id_restaurant' in kwargs:
        id_restaurant = kwargs['id_restaurant']
    else:
        id_restaurant = get_id(restaurants)

    filename = 'restaurant' + str(id_restaurant) + '.jpg'

    if 'logo' in request.files:
        if request.files['logo'].filename != '':
            logo = request.files['logo'].read()
            fs = gridfs.GridFS(db)
            if fs.exists(filename=filename):
                fs.delete(filename)
            fs.put(logo, filename=filename)

    restaurant = Restaurant(id_restaurant, username, email, password, description, address, category, filename)
    return restaurant

def set_product(request, *args, **kwargs):

    products = db['products']

    if 'id_product' in kwargs:
        id_product = kwargs['id_product']
    else:
        id_product = get_id(products)

    filename = 'product' + str(id_product) + '.jpg'

    if 'image' in request.files:
        if request.files['image'].filename != '':
            image = request.files['image'].read()
            fs = gridfs.GridFS(db)
            if fs.exists(filename=filename):
                fs.delete(filename)
            fs.put(image, filename=filename)
        
    product = Product(id_product, request.form['name'], request.form['description'], request.form['price'], filename)

    return product

@app.route('/image/<filename>')
def image(filename):
    fs = gridfs.GridFS(db)
    image = fs.get_last_version(filename=filename)
    return send_file(image, mimetype='image/jpg')

if __name__ == '__main__':
    app.run(port=4000, debug=True)