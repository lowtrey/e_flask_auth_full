from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

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

# User Profile
@app.route("/users/<username>")
def show_user(username):
  if "username" not in session:
    flash("Please log in first.", "warning")
    return redirect("/login")

  user = User.query.filter_by(username=username).first()
  return render_template("user.html", user=user)

# Register User
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
    session["username"] = new_user.username
    db.session.add(new_user)
    db.session.commit()

    flash("New User Created!", "success")
    return redirect(f"/users/{username}")
  else:
    return render_template("register.html", form=form)

# Login User
@app.route("/login", methods=["GET", "POST"])
def login_user():
  form = LoginForm()

  if form.validate_on_submit():
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    if user:
      session["username"] = user.username
      flash(f"Welcome Back, {user.username}!", "info")
      return redirect(f"/users/{user.username}")
    else:
      form.username.errors = ["Invalid username or password."]
      
  return render_template("login.html", form=form)

# Logout User
@app.route("/logout")
def logout_user():
  session.pop("username")
  flash("Logged out successfully.", "info")
  return redirect("/")

# Delete User
@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
  if "username" not in session:
    flash("You must be logged in to do that.", "warning")
    return redirect("/login")
  else:
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("User deleted successfully", "success")
    return redirect("/")

# CREATE Feedback
@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
  if "username" not in session:
    flash("You must be logged in to do that.", "warning")
    return redirect("/login")

  form = FeedbackForm()

  if form.validate_on_submit():
    title = form.title.data
    content = form.content.data

    new_feedback = Feedback(title=title, content=content, username=username)

    db.session.add(new_feedback)
    db.session.commit()

    flash("New Feedback Given!", "info")
    return redirect(f"/users/{username}")

  else:
    return render_template("add_feedback_form.html", form=form)

# Update Feedback
@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def edit_feedback(id):
  if "username" not in session:
    flash("You must be logged in to do that.", "warning")
    return redirect("/login")

  feedback = Feedback.query.get_or_404(id)
  current_username = session["username"]

  if feedback.username != current_username:
    flash("You don't have permission to do that.", "warning")
    return redirect(f"/users/{current_username}")

  form = FeedbackForm(obj=feedback)

  if form.validate_on_submit():
    feedback.title = form.title.data
    feedback.content = form.content.data

    db.session.add(feedback)
    db.session.commit()

    flash("Feedback updated successfully.", "success")
    return redirect(f"/users/{current_username}")

  else:
    return render_template("edit_feedback_form.html", form=form)

# DELETE Feedback
@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
  if "username" not in session:
    flash("You must be logged in to do that.", "warning")
    return redirect("/login")

  feedback = Feedback.query.get_or_404(id)
  current_username = session["username"]

  if feedback.username != current_username:
    flash("You don't have permission to do that.", "warning")
    return redirect(f"/users/{current_username}")

  db.session.delete(feedback)
  db.session.commit()

  flash("Feedback deleted.", "info")
  return redirect(f"/users/{current_username}")