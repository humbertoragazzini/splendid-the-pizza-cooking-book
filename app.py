"""
importing os, flask.
"""
import os
from flask import (
    Flask, flash,
    render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

"""
decorator and fuction to show tring in the app
"""


@app.route("/")
@app.route("/home_page")
def home_page():
    pizzas = mongo.db.products.find()
    return render_template("home.html", pizzas=pizzas)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("User already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check for user in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                flash("Incorrect user name or password")
                return redirect(url_for("login"))
        else:
            # username doesnt exist
            flash("Incorrect user name or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # remove session
    flash("Your are successfully logout!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    pizzas = mongo.db.recipes.find({"user":session["user"]})

    if session["user"]:
        return render_template("profile.html", username=username, pizzas=pizzas)

    return redirect(url_for("login"))


@app.route("/addrecipe")
def addrecipe():
    return render_template("addrecipe.html")


@app.route("/addrecipefirst", methods=["GET", "POST"])
def addrecipefirst():
    if request.method == "POST":

        number_of_steps = request.form.get("steps")
        ingredients = request.form.get("ingredients")
        tools = request.form.get("tools")    
        
        if number_of_steps != "0" and ingredients !="0" and tools !="0":
            categories = mongo.db.categories.find()
            return render_template("addrecipe.html", tools=tools, ingredients=ingredients, steps=number_of_steps, categories=categories)
        else:
            flash("Please, select the number of steps")
    return render_template("addrecipefirst.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

