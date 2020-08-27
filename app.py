from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import UserForm, LoginForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_full"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()

@app.route("/")
def show_index():
  return redirect("/register")

# Secret Route
@app.route("/secret")
def show_secret():
  return render_template("secret.html")

# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register_user():
  form = UserForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data

    # TODO: Add error handling for taken usernames and emails
    new_user = User.register(username, password, email, first_name, last_name)

    db.session.add(new_user)
    db.session.commit()

    flash("New User Created!", "success")
    return redirect("/secret")
  else:
    return render_template("register.html", form=form)

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login_user():
  form = LoginForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    if user:
      flash(f"Welcome Back, {user.username}!", "info")
      return redirect("/secret")
    else:
      form.username.errors = ["Invalid username or password."]
      
  return render_template("login.html", form=form)