"""
importing os, flask.
"""
import os
from flask import Flask
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

"""
decorator and fuction to show tring in the app
"""


@app.route("/")
def hello():
    return "hello pizza"


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
