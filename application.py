import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

BAGGAGES = {}

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///travel.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
            
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to log in
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        # Ensure username was submitted
        if not name:
            return apology("must provide username")

        username_exists = db.execute("SELECT username FROM users WHERE username = ?", name)
        if username_exists:
            return apology("username already exists")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        if not request.form.get("confirmation"):
            return apology("confirm your password")

        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("the passwords do not match")

        register = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, password)
        session["user_id"] = register

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    user_id = session["user_id"]
    if request.method == 'POST':
        if not request.form.get("name"):
            return apology("must provide trip's name")
        if not request.form.get("town"):
            return apology("must provide town")
        if not request.form.get("country"):
            return apology("must provide country")
        if not request.form.get("arrive"):
            return apology("must provide arrive date")
        if not request.form.get("departure"):
            return apology("must provide departure date")
        
        name = request.form.get("name")
        town = request.form.get("town")
        country = request.form.get("country")
        arrive_date = request.form.get("arrive")
        departure_date = request.form.get("departure")
        db.execute("INSERT INTO trips (user_id, name, town, country, arrive_date, departure_date) VALUES(?, ?, ?, ?, ?, ?)", 
                   user_id, name, town, country, arrive_date, departure_date)
        return redirect("/future")

    else:
        return render_template("add.html")


@app.route("/future")
@login_required
def future():
    user_id = session["user_id"]
    today = date.today()
    trips = db.execute("SELECT * FROM trips WHERE user_id = ? AND arrive_date >= ?", user_id, today)
    for trip in trips:
        trip["name"] = trip["name"]
        trip["town"] = trip["town"]
        trip["country"] = trip["country"]
        trip["arrive"] = trip["arrive_date"]
        trip["departure"] = trip["departure_date"]

    return render_template("future.html", trips=trips)


@app.route("/past")
@login_required
def past():
    today = date.today()
    user_id = session["user_id"]
    trips = db.execute("SELECT * FROM trips WHERE user_id = ? and arrive_date < ?", user_id, today)
    for trip in trips:
        trip["name"] = trip["name"]
        trip["town"] = trip["town"]
        trip["country"] = trip["country"]
        trip["arrive"] = trip["arrive_date"]
        trip["departure"] = trip["departure_date"]
    return render_template("past.html", trips=trips)


@app.route("/baggage", methods=["POST", "GET"])
@login_required
def baggage():

    user_id = session["user_id"]

    if request.method == 'POST':
        name = request.form.get("name")
        item = request.form.get('item')
        
        if not name:
            return apology("choose trip's name")
        if not item:
            return apology("must provide an item")
        
        user_id = session['user_id']
        trip_id = db.execute("SELECT id FROM trips WHERE name = ? AND user_id = ?", name, user_id)[0]['id']
        db.execute("INSERT INTO baggages (trip_id, item) VALUES(?, ?)", trip_id, item)
        trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
        options = []
        for trip in trips:
            options.append(trip['name'])
        return render_template("baggage.html", options=options)

    else:
        trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
        options = []
        for trip in trips:
            options.append(trip['name'])

        return render_template("baggage.html", options=options)


@app.route("/baggages", methods=["POST", "GET"])
@login_required
def baggages():
    if request.method == 'POST':
        name = request.form.get("name")
        check = request.form.get("check")
        
        if not name:
            return apology("choose trip's name")

        if name:
       
            user_id = session['user_id']    
            trip_id = db.execute("SELECT id FROM trips WHERE name = ? AND user_id = ?", name, user_id)[0]['id']
            items = db.execute("SELECT * FROM baggages WHERE trip_id = ?", trip_id)
            trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
            options = []
            for trip in trips:
                options.append(trip['name'])
    
            return render_template("baggages.html", items=items, options=options)
        
    else:
        user_id = session['user_id']
        trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
        options = []
        for trip in trips:
            options.append(trip['name'])

        return render_template("baggages.html", item=[], options=options)


@app.route("/check/<string:id>", methods=["POST", "GET"])
@login_required
def check(id):  
    if request.method == "POST":

        currentObj = db.execute("SELECT * FROM baggages WHERE id = ?", id)[0]
        
        if currentObj['taken'] == 'FALSE':
            newFlag = 'TRUE'  
        else: 
            newFlag = 'FALSE'
        db.execute("UPDATE baggages SET taken = ? WHERE id = ?", newFlag, id)

        items = db.execute("SELECT * FROM baggages WHERE trip_id = ?", currentObj['trip_id'])
        user_id = session['user_id']
        trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
        options = []
        for trip in trips:
            options.append(trip['name'])

        return render_template("baggages.html", items=items, options=options)
    
    else:
        user_id = session['user_id']
        trips = db.execute("SELECT DISTINCT name FROM trips WHERE user_id = ?", user_id)
        options = []
        for trip in trips:
            options.append(trip['name'])

        return render_template("baggages.html", item=[], options=options)  
  
        
@app.route("/delete/<string:id>", methods=["POST", "GET"])
@login_required
def delete(id):
    if request.method == "POST":
        db.execute("DELETE FROM trips WHERE id = ?", id)
        return redirect('/future')
    else: 
        return render_template("future.html")


@app.route("/delete_bag/<string:id>", methods=["POST", "GET"])
@login_required
def delete_bag(id):
    if request.method == "POST":
        db.execute("DELETE FROM baggages WHERE id = ?", id)
        return redirect('/baggages')
    else: 
        return render_template("baggages.html")


@app.route("/edit/<string:id>", methods=["POST", "GET"])
@login_required
def edit(id):
    if request.method == "POST":
        name = request.form.get("name")
        town = request.form.get("town")
        country = request.form.get("country")
        arrive_date = request.form.get("arrive")
        departure_date = request.form.get("departure")
        db.execute("UPDATE trips SET name = ?, town = ?, country = ?, arrive_date = ?, departure_date = ? WHERE id = ?", 
                   name, town, country, arrive_date, departure_date, id)
        return redirect("/future")
    else:
        trips = db.execute("SELECT * FROM trips WHERE id = ?", id)
        for trip in trips:
            trip["name"] = trip["name"]
            trip["town"] = trip["town"]
            trip["country"] = trip["country"]
            trip["arrive"] = trip["arrive_date"]
            trip["departure"] = trip["departure_date"]
        return render_template("edit.html", trips=trips)