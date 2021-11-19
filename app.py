'''
    importing os, flask.
'''
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


@app.route("/")
@app.route("/home_page")
def home_page():
    '''home page render'''
    return render_template("home.html")


@app.route("/")
@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    '''take the recipes from db and render templates with all recipes'''
    allrecipes = list(mongo.db.recipes.find())
    categories = list(mongo.db.categories.find())
    products = list(mongo.db.products.find())

    if request.method == "POST":
        option = request.form.get("category_name")

        if option == "all":
            allrecipes = list(mongo.db.recipes.find())
            if len(allrecipes) == 0:
                flash("No " + option + " recipes at the moment")
            return render_template(
                "recipes.html", recipes=allrecipes,
                categories=categories, products=products)

        else:
            allrecipes = list(mongo.db.recipes.find(
                {"category": option}))
            if len(allrecipes) == 0:
                flash("No (" + option + ") recipes at the moment")
            return render_template("recipes.html",
                                   recipes=allrecipes,
                                   categories=categories,
                                   products=products)

    return render_template("recipes.html",
                           recipes=allrecipes,
                           categories=categories,
                           products=products)


@app.route("/")
@app.route("/viewrecipe/<_id>")
def viewrecipe(_id):
    '''render view recipe page with the recipe selected'''
    print(_id)
    products = list(mongo.db.products.find())
    recipetoview = list(mongo.db.recipes.find({"_id": ObjectId(_id)}))
    return render_template("viewrecipe.html",
                           recipetoview=recipetoview,
                           products=products)


@app.route("/")
@app.route("/aboutus")
def aboutus():
    '''render the about us with some company info'''
    return render_template("aboutus.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    '''
    render register page and take with
    a post metod all the data from the form
    '''
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("User already exists")
            return redirect(url_for("register"))

        newregister = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(newregister)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        products = list(mongo.db.products.find())
        return redirect(url_for("profile",
                                username=session["user"],
                                products=products))
    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    '''
    render login page and take the login
    details from the form to check with the db
    '''
    if request.method == "POST":
        # check for user in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                products = list(mongo.db.products.find())
                return redirect(url_for("profile",
                                        username=session["user"],
                                        products=products))
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
    '''close the session'''
    # remove session
    flash("Your are successfully logout!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    '''
    render the profile page with all the recipes
    is an admin render with all the recipes
    '''
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    pizzas = mongo.db.recipes.find({"user": session["user"]})

    if session["user"] == "admin":
        pizzas = mongo.db.recipes.find()
        products = list(mongo.db.products.find())
        return render_template("profile.html",
                               username=username,
                               pizzas=pizzas,
                               products=products)
    if session["user"]:
        products = list(mongo.db.products.find())
        return render_template("profile.html",
                               username=username,
                               pizzas=pizzas,
                               products=products)

    return redirect(url_for("login"))


@app.route("/addrecipe", methods=["GET", "POST"])
def addrecipe():
    '''
    render de add recipe page and if is
    post take all data from form to send it to the db
    '''
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

            for step_number in tools_igredient_indexer:

                if request.form.get("step"+str(step_number)):

                    new_recipe["step"+str(step_number)] = request.form.get(
                        "step"+str(step_number))

            for ingredient_number in tools_igredient_indexer:

                if request.form.get("ingredient"+str(ingredient_number)):

                    new_recipe[
                        "ingredient"+str(ingredient_number)] = \
                            request.form.get(
                                "ingredient"+str(ingredient_number))

            for tool_number in tools_igredient_indexer:

                if request.form.get("tool"+str(tool_number)):

                    new_recipe["tool"+str(tool_number)] = \
                        request.form.get(
                            "tool"+str(tool_number))

            mongo.db.recipes.insert_one(new_recipe)

            flash("Recipe added successful!")
        products = list(mongo.db.products.find())
        return redirect(url_for("profile",
                                username=session["user"],
                                products=products))

    return render_template("addrecipe.html")


@app.route("/delete/<recipe_id>", methods=["GET", "POST"])
def delete(recipe_id):
    '''
    delete the recipe from db and reload recipe list
    '''
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    pizzas = mongo.db.recipes.find({"user": session["user"]})

    if session["user"]:
        if session["user"] == "admin":
            pizzas = mongo.db.recipes.find()
        products = list(mongo.db.products.find())
        return render_template("profile.html",
                               username=username,
                               pizzas=pizzas,
                               products=products)

    return render_template("login.html")


@app.route("/addrecipefirst", methods=["GET", "POST"])
def addrecipefirst():
    '''
    render add recipe first, its the first step,
    send category n of steps, tools, and ingredients to addrecipe
    '''
    if request.method == "POST":

        number_of_steps = request.form.get("steps")
        ingredients = request.form.get("ingredients")
        tools = request.form.get("tools")

        if number_of_steps != "0" and ingredients != "0" and tools != "0":
            categories = mongo.db.categories.find()
            return render_template("addrecipe.html",
                                   tools=tools,
                                   ingredients=ingredients,
                                   steps=number_of_steps,
                                   categories=categories)
        else:
            flash("Please, select the number of steps")
    return render_template("addrecipefirst.html")


@app.route("/editrecipe/<recipe_name>", methods=["GET", "POST"])
def editrecipe(recipe_name):
    '''
    render edit recipe and take data from form to update db
    '''
    recipe = list(mongo.db.recipes.find({"tittle": recipe_name}))
    user_recipes = list(mongo.db.recipes.find({"user": session['user']}))
    categories = mongo.db.categories.find()
    extractvalues = recipe[0]
    product_id = extractvalues["_id"]

    if request.method == "POST":

        tools_igredient_indexer = range(12)
        if session["user"] == "admin":
            user_recipes = list(mongo.db.recipes.find())
            new_recipe = {
                "user": request.form.get("username").lower(),
                "tittle": request.form.get("tittle").lower(),
                "category": request.form.get("category_name"),
                "description": request.form.get("description"),
            }
        else:
            new_recipe = {
                "user": extractvalues["user"],
                "tittle": request.form.get("tittle").lower(),
                "category": request.form.get("category_name"),
                "description": request.form.get("description"),
            }

        for step_number in tools_igredient_indexer:

            if request.form.get("step"+str(step_number)):

                new_recipe["step"+str(step_number)] = \
                    request.form.get("step"+str(step_number))

        for ingredient_number in tools_igredient_indexer:

            if request.form.get("ingredient"+str(ingredient_number)):

                new_recipe["ingredient"+str(ingredient_number)] = \
                    request.form.get(
                        "ingredient"+str(ingredient_number))

        for tool_number in tools_igredient_indexer:

            if request.form.get("tool"+str(tool_number)):

                new_recipe["tool"+str(tool_number)] = \
                    request.form.get("tool"+str(tool_number))

        mongo.db.recipes.update({"_id": ObjectId(product_id)}, new_recipe)

        flash("Recipe edited successful!")
        products = list(mongo.db.products.find())
        return redirect(url_for("profile",
                                username=session["user"],
                                products=products,
                                reicpes=user_recipes))

    return render_template("editrecipe.html",
                           recipe=recipe,
                           categories=categories)


@app.route("/addoffer", methods=["GET", "POST"])
def addoffer():
    '''
    render addoffer panel to add products
    and male them popups for the regular users
    '''
    if request.method == "POST":
        existing_product_name = mongo.db.products.find_one(
            {"product_name": request.form.get("product_name").lower()})

        if existing_product_name:
            flash("Product already exists in the promotion offers")
        else:
            new_offer = {
                "user": session["user"],
                "product_name": request.form.get("product_name").lower(),
                "description": request.form.get("description"),
                "url": request.form.get("url"),
            }
            mongo.db.products.insert_one(new_offer)
            flash("Product added!")

    return render_template("addoffer.html")


@app.route("/adminpanel/<username>")
def adminpanel(username):
    '''
    render the admin control panel
    '''
    return render_template("adminpanel.html", username=username)


@app.route("/removeproductpanel")
def removeproductpanel():
    '''
    render the remove product panel to delete products from db
    '''
    products = list(mongo.db.products.find())
    return render_template("removeproductpanel.html", products=products)


@app.route("/deleteproduct/<product_id>", methods=["GET", "POST"])
def deleteproduct(product_id):
    '''
    remove the products from db and update list of products
    '''
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    products = mongo.db.products.find({"user": session["user"]})

    if session["user"]:
        return render_template("removeproductpanel.html",
                               username=username,
                               products=products)

    return render_template("login.html")


@app.route("/removeuserpanel")
def removeuserpanel():
    '''
    render remove user panel with the recipes of the users
    '''
    users = list(mongo.db.users.find())
    user_recipes = list(mongo.db.recipes.find())
    return render_template("removeuserpanel.html",
                           users=users,
                           recipes=user_recipes)


@app.route("/deleteuser/<user_id>", methods=["GET", "POST"])
def deleteuser(user_id):
    '''
    render delete user panel to make a list of users
    '''
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    users = list(mongo.db.users.find())
    user_recipes = list(mongo.db.recipes.find())

    if session["user"]:
        return render_template("removeuserpanel.html",
                               username=username,
                               users=users,
                               recipes=user_recipes)

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
