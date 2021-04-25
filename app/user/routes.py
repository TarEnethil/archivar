from app import db
from app.decorators import admin_required
from app.helpers import page_title, Role, deny_access
from app.user import bp
from app.user.forms import CreateUserForm, EditProfileForm, SettingsForm, PasswordOnlyForm
from app.user.helpers import gen_role_choices
from app.user.models import User
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from werkzeug import check_password_hash

no_perm_url = "main.index"


@bp.route("/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template("user/profile.html", user=user, title=page_title(f"View User '{user.username}'"))


# TODO: Fix C901
@bp.route("/<username>/edit", methods=["GET", "POST"])
@login_required
def edit(username):  # noqa: C901
    user = User.query.filter_by(username=username).first_or_404()

    if not user.is_editable_by_user():
        return deny_access(no_perm_url)

    form = EditProfileForm()

    if current_user.is_admin():
        form.role.choices = gen_role_choices()
    else:
        del form.role

    if form.validate_on_submit():
        user.about = form.about.data

        if(form.password.data):
            user.set_password(form.password.data)

            if current_user.username == user.username:
                user.must_change_password = False
            elif current_user.is_admin():
                # user must reset password after it has been changed by an admin
                user.must_change_password = True

        role_okay = True

        if current_user.is_admin():
            old_role = user.role
            new_role = form.role.data

            if username == current_user.username and current_user.is_admin() and new_role != Role.Admin.value:
                flash("You can't revoke your own admin role.", "danger")
                role_okay = False
            elif user.id == 1 and new_role != Role.Admin.value:
                flash("The original admin can't be removed.", "danger")
                role_okay = False
            else:
                user.role = new_role

        if role_okay:
            db.session.commit()
            flash("Your changes have been saved.", "success")

            return redirect(user.view_url())
        else:
            form.role.data = old_role
    elif request.method == "GET":
        form.about.data = user.about

        if current_user.is_admin():
            form.role.data = user.role

    return render_template("user/edit.html", form=form, user=user, title=page_title(f"Edit User '{user.username}'"))


@bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required(no_perm_url)
def create():
    form = CreateUserForm()

    form.role.choices = gen_role_choices()

    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        new_user.role = form.role.data
        new_user.created = datetime.utcnow()

        db.session.add(new_user)
        db.session.commit()

        flash("New user " + new_user.username + " created.", "success")
        return redirect(new_user.view_url())
    else:
        return render_template("user/create.html", form=form, title=page_title("Add User"))


@bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    form = PasswordOnlyForm()

    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.password.data):
            flash("You must choose a different password.", "danger")
        else:
            current_user.set_password(form.password.data)
            current_user.must_change_password = False
            flash("Password was changed.", "success")

        db.session.commit()

        return redirect(url_for('index'))

    return render_template("user/password.html", form=form, title=page_title("Change Password"))


@bp.route("/list")
@login_required
@admin_required(no_perm_url)
def list():
    users = User.query.all()

    return render_template("user/list.html", users=users, title=page_title("User List"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        current_user.dateformat = form.dateformat.data
        current_user.editor_height = form.editor_height.data
        current_user.markdown_phb_style = form.markdown_phb_style.data
        current_user.quicklinks = form.quicklinks.data

        flash("Settings changed.", "success")

        db.session.commit()
    elif request.method == "GET":
        form.dateformat.data = current_user.dateformat
        form.editor_height.data = current_user.editor_height
        form.markdown_phb_style.data = current_user.markdown_phb_style
        form.quicklinks.data = current_user.quicklinks

    return render_template("user/settings.html", form=form, title=page_title("User Settings"))
