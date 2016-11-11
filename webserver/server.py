#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

	python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
# DATABASEURI = "sqlite:///test.db"
DATABASEURI = "postgresql://yw2902:pt3hu@104.196.175.120/postgres"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test ( id serial, name text);""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#


app.secret_key = 'what'


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print request.args

    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT name FROM customer")
    names = []
    for result in cursor:
        names.append(result['name'])  # can also be accessed using result[0]	
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be 
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #     
    #     # creates a <div> tag for each element in data
    #     # will print: 
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #    {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data = names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
	return render_template("anotherfile.html")


@app.route('/store')
def store():
    cursor = g.conn.execute("select p.pid, p.name as product, p.price, p.weight, s.name as supplier, sh.name as shipper, sh.shiprate from product as p, product_supplier as ps, supplier as s, shipper as sh, partner as pa where ps.pid = p.pid and ps.sid = s.sid and pa.shid = sh.shid and pa.sid = s.sid")
    products = []
    for product in cursor:
        products.append([product['pid'], product['product'], product['price'], product['weight'], product['supplier'], product['shipper'], product['shiprate']])
    context = dict(data=products)
    return render_template("store.html", **context)



@app.route('/review')
def review():
    cursor = g.conn.execute("SELECT c.name customer, p.name product, r.comment review, r.date  FROM review r, customer c, product p where p.pid = r.pid and r.cid = c.cid")
    reviews = []
    for review in cursor:
        reviews.append([review['customer'], review['product'], review['date'], review['review']] )

    cursor = g.conn.execute("SELECT pid, name FROM PRODUCT")
    products = [];
    for product in cursor:
        products.append([product['pid'], product['name']])

    context = dict(data=reviews, productkey=products)
    return render_template("review.html", **context)




# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print name
    cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
    g.conn.execute(text(cmd), name1 = name, name2 = name);
    return redirect('/')


@app.route('/postreview', methods=["GET", "POST"])
def postReview():
    email = request.form['email']
    password = request.form['password']
    pid = request.form['selectbox3']
    review = request.form['message']

    # first use email to get cid
    cursor = g.conn.execute("SELECT c.cid FROM CUSTOMER c WHERE c.email = %s and c.password = %s", (email, password))
    cid = cursor.fetchone()['cid']

    g.conn.execute("INSERT INTO review(cid, date, comment, pid) VALUES (%s, %s, %s, %s)", (cid, str(datetime.date.today()), review, pid ))
    print review
    return redirect('/review')


@app.route('/placeorder', methods=['GET', 'POST'])
def placeorder():
    email = request.form['email']
    password = request.form['password']
    totalprice = request.form['totalprice']
    allproducts = request.form['allproducts'].split('|')

    # first get cid from email and password
    cid = g.conn.execute("SELECT cid FROM customer WHERE email=%s AND password=%s", (email, password)).fetchone()['cid']
    # then get its aid from live table
    aid = g.conn.execute("SELECT aid FROM live WHERE cid=%s", (cid)).fetchone()['aid']
    # finally insert into orders table
    g.conn.execute("INSERT INTO orders(total_price, date,  cid, aid) VALUES (%s, %s, %s, %s) ", (float(totalprice), str(datetime.date.today()), cid, aid))

    # get the current oid
    oid = g.conn.execute("SELECT max(oid) oid FROM orders").fetchone()['oid']
    # insert into order_product
    for product in allproducts:
        tmp = product.split('*')
        pid, quantity = tmp[0], tmp[1]
        g.conn.execute("INSERT INTO order_product VALUES(%s, %s, %s)", (oid, pid, quantity))

    return redirect('/store')


@app.route('/UserSignup', methods=['POST'])
def userSignup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    # insert into customer table
    args = (username, email, password)
    cursor = g.conn.execute("INSERT INTO customer(name, email, password) VALUES(%s, %s, %s)", args)
    cid = g.conn.execute("SELECT * FROM CUSTOMER WHERE name = %s and email = %s and password = %s", args ).fetchone()['cid']

    # address table insert
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']
    streetaddress = request.form['streetaddress']
    zipcode = request.form['zipcode']
    args = (country, state, city, streetaddress, zipcode)
    cursor = g.conn.execute("SELECT a.aid FROM ADDRESS a WHERE a.country = %s and a.state = %s and a.city = %s and a.street_address = %s and a.zip = %s", args)

    if cursor.rowcount==0:
    	g.conn.execute('INSERT INTO address(country, state, city, street_address, zip) VALUES (%s, %s, %s, %s, %s)', args)
    	aid = g.conn.execute("SELECT a.aid FROM ADDRESS a WHERE a.country = %s and a.state = %s and a.city = %s and a.street_address = %s and a.zip = %s", args).fetchone()['aid']
    else:
    	aid = cursor.fetchone()['aid']
    
    # insert live table
    g.conn.execute("INSERT INTO live VALUES(%s, %s)", (cid, aid))


    # # check whether address already exists
    # if cursor.fetchone() is None:
    # 	g.conn.execute('INSERT INTO address(country, state, city, street_address, zip) VALUES (%s, %s, %s, %s, %s)', args)
    # 	aid = g.conn.execute("SELECT a.aid FROM ADDRESS a WHERE a.country = %s and a.state = %s and a.city = %s and a.street_address = %s and a.zip = %s", args).fetchone()['aid']
    # else:
    # 	print cursor.previous()
    # 	aid = cursor.previous()['aid']

    # if(cursor.rowcount==0):
    #     # insert into address table
    #     args = (country, state, city, streetaddress,zipcode )
    #     g.conn.execute('INSERT INTO address(country, state, city, street_address, zip) VALUES (%s, %s, %s, %s, %s)', args)
    #     aid = g.conn.execute('SELECT MAX(aid) FROM ADDRESS').fetchone()['aid']
    # else:
    #     aid = cursor.fetchone()['aid']


    # # insert into live table
    # pid = g.conn.execute('SELECT')
    # g.conn.execute('INSERT INTO live VALUES( (SELECT max(cid) FROM customer), (SELECT max(aid) FROM address))')


    #cmd = 'INSERT INTO customer(name, email, password) VALUES (:username),(:email), (:password)';
    #g.conn.execute(text(cmd), username = request.form['username'], email = request.form['email'], password= request.form['password']);
    
    return redirect('/store')


@app.route('/viewprofile', methods=['POST'])
def viewprofile():
    email, password = request.form['email'], request.form['password']
    record = g.conn.execute("SELECT cid, name FROM CUSTOMER WHERE email=%s AND password=%s", (email, password)).fetchone()
    cid, name = record['cid'], record['name']
    curaid = g.conn.execute("SELECT aid FROM live WHERE cid=%s", (cid)).fetchone()['aid']
    tmp = g.conn.execute("SELECT * FROM ADDRESS WHERE aid = %s", (curaid)).fetchone()
    curaddress = tmp['street_address'] + ' ' + tmp['city'] + ' ' + tmp['state'] + tmp['zip'] + ' ' + tmp['country']

    profile = [name, curaddress, email, password]

    #get all orders information
    cursor = g.conn.execute("SELECT * FROM orders WHERE cid = %s", (cid))
    orders = []
    for order in cursor:
        oid, date, aid, totalprice = order['oid'], order['date'], order['aid'], order['total_price']
        tmp = g.conn.execute("SELECT * FROM ADDRESS WHERE aid = %s", (aid)).fetchone()
        address = tmp['street_address'] + ' ' + tmp['city'] + ' ' + tmp['state'] + tmp['zip'] + ' ' + tmp['country']
        print address
        # get all tuples (product & quantity) of this oid
        pqs = g.conn.execute("SELECT pid, quantity FROM order_product WHERE oid = %s", (oid))
        products = ""
        for pq in pqs:
            productname = g.conn.execute("SELECT name FROM product WHERE pid = %s ", (pq['pid'])).fetchone()['name']
            products += ' ' + str(pq['quantity']) + ' * ' + str(productname) + '; '

        orders.append([date, products, address,totalprice])

    context = dict(orderskey=orders, profilekey=profile)
    return render_template("viewprofile.html", **context)


@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/getUpdateProfile', methods=["GET", "POST"])
def getUpdateProfile():
    email, password = request.form['email'], request.form['password']
    context=dict(profile=[email, password])

    return render_template("updateProfile.html", **context)


@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    email, password, username = request.form['email'], request.form['password'], request.form['username']
    country, state, city, streetaddress, zipcode = request.form['country'], request.form['state'], request.form['city'], request.form['streetaddress'], request.form['zipcode']
    g.conn.execute("UPDATE customer SET password=%s, name=%s WHERE email=%s", (password, username, email))
    count = g.conn.execute("SELECT count(*) FROM address WHERE country=%s AND state=%s AND city=%s AND street_address=%s AND zip=%s", (country, state, city, streetaddress, zipcode)).fetchone()['count'];
    print "count=", count

    # the address doesn't exist in the database, create new address
    if count==0:
        g.conn.execute("INSERT INTO address(country, state, city, street_address, zip) VALUES(%s, %s, %s, %s, %s)", (country, state, city, streetaddress, zipcode))
    aid = g.conn.execute("SELECT aid FROM address WHERE country=%s AND state=%s AND city=%s AND street_address= %s and zip= %s", (country, state, city, streetaddress, zipcode)).fetchone()['aid']
    cid = g.conn.execute("SELECT cid FROM customer WHERE email = %s", (email)).fetchone()['cid']
    g.conn.execute("UPDATE live SET aid = %s WHERE cid = %s", (aid, cid))
    return redirect('/store')


@app.route('/toDelete')
def toDelete():
    return render_template("deleteAccount.html")


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    email, password = request.form['email'], request.form['password']
    g.conn.execute("DELETE FROM customer WHERE email=%s AND password=%s", (email, password))
    return redirect('/store')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 404



# @app.route('/login')
# def login():
#     # abort(401)
#     # this_is_never_executed()
#     return render_template("login.html")


# @app.route('/loguserin', methods=['GET', 'POST'])
# def loguserin():
#     email, password = request.form['email'], request.form['password']
#     print email, password

#     cursor = g.conn.execute("SELECT email, password FROM CUSTOMER")
#     users = []
#     loginSuccess = False
#     for row in cursor:
#         if email == row['email'] and password == row['password']:
#             loginSuccess = True
#     if loginSuccess == False:
#         flash("<p>No user found</p>")
#     else:
#         flash('You were logged in')
#         print session
#         return redirect('/store')
#     return render_template('/login.html')


if __name__ == "__main__":
    import click
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

        python server.py

        Show the help text using

        python server.py --help
        """
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()