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
    pizzas = list(mongo.db.recipes.find())
    return render_template("home.html", pizzas=pizzas)


@app.route("/")
@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    recipes = list(mongo.db.recipes.find())
    categories = list(mongo.db.categories.find())

    if request.method == "POST":
        option = request.form.get("category_name")

        if option == "all":
            recipes = list(mongo.db.recipes.find())
            return render_template("recipes.html", recipes=recipes, categories=categories)
        
        else:
            recipes = list(mongo.db.recipes.find(
                {"category": option }))
            return render_template("recipes.html", recipes=recipes, categories=categories)

    return render_template("recipes.html", recipes=recipes, categories=categories)


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
    
    pizzas = mongo.db.recipes.find({"user": session["user"]})

    if session["user"]:
        return render_template("profile.html", username=username, pizzas=pizzas)

    return redirect(url_for("login"))


@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    if request.method == "POST":
        existing_recipe_name = mongo.db.recipes.find_one(
            {"tittle": request.form.get("tittle").lower()})

        if existing_recipe_name:
            flash("Recipe name already exists")
        else:
            tools_igredient_indexer = range(12)

            new_recipe = {
                "user": session["user"],
                "tittle": request.form.get("tittle").lower(),
                "category": request.form.get("category_name"),
                "description": request.form.get("description"),
            }

            for n in tools_igredient_indexer:
                
                if request.form.get("step"+str(n)):
                    
                    new_recipe["step"+str(n)] = request.form.get("step"+str(n))

            for n in tools_igredient_indexer:
                
                if request.form.get("ingredient"+str(n)):
                    
                    new_recipe["ingredient"+str(n)] = request.form.get("ingredient"+str(n))

            for n in tools_igredient_indexer:
                
                if request.form.get("tool"+str(n)):
                    
                    new_recipe["tool"+str(n)] = request.form.get("tool"+str(n))

            mongo.db.recipes.insert_one(new_recipe)

        flash("Recipe added successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("addrecipe.html")


@app.route("/addrecipefirst", methods=["GET", "POST"])
def addrecipefirst():
    if request.method == "POST":

        number_of_steps = request.form.get("steps")
        ingredients = request.form.get("ingredients")
        tools = request.form.get("tools")    
        
        if number_of_steps != "0" and ingredients != "0" and tools != "0":
            categories = mongo.db.categories.find()
            return render_template("addrecipe.html", tools=tools, ingredients=ingredients, steps=number_of_steps, categories=categories)
        else:
            flash("Please, select the number of steps")
    return render_template("addrecipefirst.html")


@app.route("/editrecipe/<recipe_name>", methods=["GET", "POST"])
def editrecipe(recipe_name):

    recipe = list(mongo.db.recipes.find({"tittle": recipe_name}))
    categories = mongo.db.categories.find()
    extractvalues = recipe[0]
    id = extractvalues["_id"]
    
    if request.method == "POST":

        tools_igredient_indexer = range(12)

        new_recipe = {
            "user": session["user"],
            "tittle": request.form.get("tittle").lower(),
            "category": request.form.get("category_name"),
            "description": request.form.get("description"),
        }

        for n in tools_igredient_indexer:

            if request.form.get("step"+str(n)):

                new_recipe["step"+str(n)] = request.form.get("step"+str(n))

        for n in tools_igredient_indexer:

            if request.form.get("ingredient"+str(n)):

                new_recipe["ingredient"+str(n)] = request.form.get("ingredient"+str(n))

        for n in tools_igredient_indexer:

            if request.form.get("tool"+str(n)):

                new_recipe["tool"+str(n)] = request.form.get("tool"+str(n))

        mongo.db.recipes.update({"_id": ObjectId(id)}, new_recipe)

        flash("Recipe edited successful!")

        return redirect(url_for("profile", username=session["user"]))

    return render_template("editrecipe.html", recipe=recipe, categories=categories)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

