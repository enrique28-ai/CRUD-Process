from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from forms.form_user import RegisterForm, LoginForm, SecurityQuestionForm, ResetPasswordForm
from utils.db import db
from models.user_model import User
from flask_login import login_user, logout_user

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if  request.method == "POST" and form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data,
                              security_question=form.security_question.data)
        user_to_create.set_security_answer(form.security_answer.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('process.index'))
    
    if form.errors:  # If there are errors
        for err_msgs in form.errors.values():  # Get only the list of error messages
            for err_msg in err_msgs:  # Iterate over each individual error
                flash(f" {err_msg}", category='danger')


    return render_template('register.html', form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('process.index'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    session.clear()
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('process.home'))

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = SecurityQuestionForm()
    user = None

    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).first()

        if user and "security_answer" in request.form:  # If the answer is submitted
            if user.check_security_answer(form.security_answer.data):
                flash("Security question verified. Please reset your password.", category="success")
                return redirect(url_for("auth.reset_password", username=user.username))
            else:
                flash("Incorrect security answer. Try again.", category="danger")
        
        elif user:  # When the username is entered, display the security question
            return render_template("forgot_password.html", form=form, user=user)

        else:
            flash("Username not found!", category="danger")

    return render_template("forgot_password.html", form=form, user=None)


@auth.route("/reset-password/<username>", methods=["GET", "POST"])
def reset_password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Invalid request", category="danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        user.password = form.password.data  # Automatically hashed
        db.session.commit()
        flash("Your password has been reset!", category="success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)

