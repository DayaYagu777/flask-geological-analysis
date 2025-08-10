from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    image = FileField('Image File', validators=[DataRequired()])
    excel_file = FileField('Excel File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class FilterForm(FlaskForm):
    phase = SelectField('Excavation Phase', choices=[], validators=[DataRequired()])
    submit = SubmitField('Filter')