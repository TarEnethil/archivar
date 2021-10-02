from app import db
from app.random import bp
from app.random.forms import RandomTableForm, RandomTableEntryForm
from app.random.models import RandomTable, RandomTableEntry
from app.helpers import page_title, deny_access
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required

no_perm_url = "random.index"


@bp.route("/", methods=["GET"])
@login_required
def index():
    tables = RandomTable.query.all()
    return render_template("random/index.html", tables=tables, title=page_title("Random Rolls"))


@bp.route("/table/create", methods=["GET", "POST"])
@login_required
def table_create():
    form = RandomTableForm()
    heading = "Create Random Table"
    form.submit.label.text = heading

    if form.validate_on_submit():
        table = RandomTable(name=form.name.data,
                            description=form.description.data)

        db.session.add(table)
        db.session.commit()
        flash("Random Table was created.", "success")

        return redirect(table.view_url())
    else:
        return render_template("random/table_form.html", heading=heading, form=form, title=page_title(heading))


@bp.route("/table/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@bp.route("/table/edit/<int:id>", methods=["GET", "POST"])
@login_required
def table_edit(id, name=None):
    table = RandomTable.query.filter_by(id=id).first_or_404()
    heading = f"Edit Random Table {table.name}"

    form = RandomTableForm()
    form.submit.label.text = "Save Random Table"

    if form.validate_on_submit():
        table.name = form.name.data
        table.description = form.description.data

        db.session.commit()
        flash("Random Table was changed.", "success")
        return redirect(table.view_url())
    else:
        form.name.data = table.name
        form.description.data = table.description
        return render_template("random/table_form.html", heading=heading, form=form, title=page_title(heading))


@bp.route("/table/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/table/view/<int:id>", methods=["GET"])
@login_required
def table_view(id, name=None):
    table = RandomTable.query.filter_by(id=id).first_or_404()
    return render_template("random/table_view.html", table=table, title=page_title(f"View Table '{table.name}'"))


@bp.route("/table/roll/<int:id>/<string:name>", methods=["GET"])
@bp.route("/table/roll/<int:id>", methods=["GET"])
@login_required
def table_roll(id, name=None):
    table = RandomTable.query.filter_by(id=id).first_or_404()

    rolls = request.args.get("num_rolls")
    if rolls:
        try:
            rolls = int(rolls)
        except ValueError:
            flash(f"{rolls} is not a valid roll number")
            return redirect(request.referrer)
    else:
        rolls = 1

    return render_template("random/table_roll.html", table=table, num_rolls=rolls,
                           title=page_title(f"Roll on Table '{table.name}'"))


@bp.route("table/delete/<int:id>/<string:name>")
@login_required
def table_delete(id, name=None):
    table = RandomTable.query.filter_by(id=id).first_or_404()

    if not table.is_deletable_by_user():
        return deny_access(no_perm_url)

    db.session.delete(table)
    db.session.commit()

    flash("Table was deleted.", "success")
    return redirect(url_for("random.index"))


@bp.route("/table/<int:t_id>/<string:t_name>/entry/create", methods=["GET", "POST"])
@login_required
def table_entry_create(t_id, t_name=None):
    table = RandomTable.query.filter_by(id=t_id).first_or_404()
    form = RandomTableEntryForm()
    heading = f"Create Random Table Entry for {table.name}"
    form.submit.label.text = "Create Entry"

    if form.validate_on_submit():
        entry = RandomTableEntry(title=form.title.data,
                                 weight=form.weight.data,
                                 description=form.description.data,
                                 table_id=form.table.data)

        db.session.add(entry)
        db.session.commit()
        flash("Random Table Entry was created.", "success")

        return redirect(table.view_url())
    else:
        form.table.data = table.id
        return render_template("random/table_entry_form.html", heading=heading, form=form, title=page_title(heading))


@bp.route("/table/<int:t_id>/<string:t_name>/entry/edit/<int:e_id>/<string:e_name>", methods=["GET", "POST"])
@bp.route("/table/<int:t_id>/<string:t_name>/entry/edit/<int:e_id>", methods=["GET", "POST"])
@login_required
def table_entry_edit(t_id, e_id, t_name=None, e_name=None):
    entry = RandomTableEntry.query.filter_by(id=e_id).first_or_404()
    heading = f"Edit Random Table Entry {entry.title}"

    form = RandomTableEntryForm()
    form.submit.label.text = "Save Entry"
    del form.table

    if form.validate_on_submit():
        entry.title = form.title.data
        entry.weight = form.weight.data
        entry.description = form.description.data

        db.session.commit()
        flash("Random Table Entry was changed.", "success")
        return redirect(entry.table.view_url())
    else:
        form.title.data = entry.title
        form.weight.data = entry.weight
        form.description.data = entry.description
        return render_template("random/table_entry_form.html", heading=heading, form=form, title=page_title(heading))


@bp.route("/table/<int:t_id>/<string:t_name>/entry/view/<int:e_id>/<string:e_name>", methods=["GET"])
@bp.route("/table/<int:t_id>/<string:t_name>/entry/view/<int:e_id>", methods=["GET"])
@login_required
def table_entry_view(t_id, e_id, t_name=None, e_name=None):
    entry = RandomTableEntry.query.filter_by(id=e_id).first_or_404()
    return render_template("random/table_entry_view.html", entry=entry,
                           title=page_title(f"View Table Entry '{entry.title}'"))


@bp.route("table/<int:t_id>/<string:t_name>/delete/<int:e_id>/<string:e_name>")
@login_required
def table_entry_delete(t_id, e_id, t_name=None, e_name=None):
    entry = RandomTableEntry.query.filter_by(id=e_id).first_or_404()
    link = entry.table.view_url()

    if not entry.is_deletable_by_user():
        return deny_access(no_perm_url)

    db.session.delete(entry)
    db.session.commit()

    flash("Entry was deleted.", "success")
    return redirect(link)
