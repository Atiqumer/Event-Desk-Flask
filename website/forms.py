from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, IntegerField, SelectField
from wtforms.fields import DateField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Optional, ValidationError, NumberRange
from flask_wtf.file import FileRequired, FileField, FileAllowed


ALLOWED_FILES = ["PNG", "JPG", "png", "jpg", "JPEG", "jpeg"]


def genre_field_check(form, field):
    if field.data == "":
        raise ValidationError("Please select a genre!")


def status_field_check(form, field):
    if field.data == "":
        raise ValidationError("Please select a status!")


class LoginForm(FlaskForm):
    user_name = StringField("User Name", validators=[
                            InputRequired('Enter user name')])
    password = PasswordField("Password", validators=[
                             InputRequired('Enter user password')])


class RegisterForm(FlaskForm):
    user_name = StringField("User Name", validators=[InputRequired(), Length(min=4)])
    email_id = StringField("Email Address", validators=[
                           InputRequired(), Email("Please enter a valid email"), Length(min=6)])
    contact = IntegerField("Contact Number", validators=[
                           InputRequired('Please enter a valid contact number')])
    address = StringField("Address", validators=[
                          InputRequired('Please enter your address'), Length(min=4)])
    password = PasswordField("Password", validators=[InputRequired(), EqualTo(
        'confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])


class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[InputRequired(), Length(min=2)])
    artist_name = StringField('Artist Name', validators=[InputRequired(), Length(min=3)])
    status = SelectField("Status", choices=[("", "--Please select status--"),
                                            ("Active", "Active"), ("Upcoming", "Upcoming"), ("Inactive", "Inactive")], validators=[status_field_check])
    genre = SelectField("Genre", choices=[("", "--Please select genre--"), ("Country", "Country"), ("Electronic", "Electronic"),
                                          ("Funk", "Funk"), ("Hiphop", "Hip Hop"), ("Jazz", "Jazz"), ("House", "House"), 
                                          ("Pop", "Pop"), ("Rap", "Rap"), ("Rock", "Rock")], validators=[genre_field_check])
    date = DateField('Date', validators=[InputRequired()])
    time = StringField("Time", validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    image = FileField('Event Image', validators=[FileRequired(), FileAllowed(
        ALLOWED_FILES, message=f"Accepted file types: {ALLOWED_FILES}")])
    price = StringField('Price', validators=[InputRequired(), Length(min=1)])
    num_tickets = IntegerField(
        "Number of Tickets", validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField()


class EventEditForm(FlaskForm):
    event_name = StringField('Event Name', validators=[])
    artist_name = StringField('Artist Name', validators=[])
    status = SelectField("Status", choices=[("", "--Please select status--"),
                                            ("Active", "Active"), ("Upcoming", "Upcoming"), ("Inactive", "Inactive")])
    genre = SelectField("Genre", choices=[("", "--Please select genre--"), ("Country", "Country"), ("Electronic", "Electronic"),
                                          ("Funk", "Funk"), ("Hiphop", "Hip Hop"), ("Jazz", "Jazz"), ("House", "House"), 
                                          ("Pop", "Pop"), ("Rap", "Rap"), ("Rock", "Rock")])
    date = DateField('Date', validators=[])
    time = StringField("Time", validators=[])
    location = StringField('Location', validators=[])
    description = TextAreaField('Description', validators=[])
    image = FileField('Event Image', validators=[FileAllowed(
        ALLOWED_FILES, message=f"Accepted file types: {ALLOWED_FILES}")])
    price = IntegerField('Price', validators=[Optional(), NumberRange(min=0)])
    num_tickets = IntegerField(
        "Number of Tickets", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField()


class CommentForm(FlaskForm):
    text = StringField('Leave a comment here!', validators=[InputRequired(), Length(min=3)])
    submit = SubmitField('Create')


class BookingForm(FlaskForm):
    num_tickets = IntegerField(
        'Number of Tickets', validators=[InputRequired(), NumberRange(min=1)])
    submit = SubmitField()