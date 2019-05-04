from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import Length, InputRequired

class WikiEntryForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(),Length(min=0, max=255)])
    category = StringField("Category", validators=[Length(min=0, max=100)])
    content = TextAreaField("Content", render_kw={"rows": 15})
    dm_content = TextAreaField("DM Notes (hidden)", render_kw={"rows": 15})
    tags = StringField("Tags", validators=[Length(min=0, max=255)])
    is_visible = BooleanField("Visible to others")

    submit = SubmitField("Submit")

class WikiSettingsForm(FlaskForm):
    default_visible = BooleanField("New wiki entries are visible by default")

    submit = SubmitField("Save settings")

class WikiSearchForm(FlaskForm):
    searchterm = StringField("", validators=[InputRequired()])
    tags = RadioField(choices=[('text', "Text"), ('tag', "Tags")], default='text')

    submit = SubmitField("Search")

class WikiMoveCategoryForm(FlaskForm):
    old_category = SelectField("Category to be renamed",validators=[InputRequired()])
    new_category = StringField("New name", validators=[Length(min=0, max=100)])

    # different name because we have two forms on the same page
    submit_move = SubmitField("Move category")