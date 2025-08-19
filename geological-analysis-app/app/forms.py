from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    image = FileField('Image File', validators=[DataRequired()])
    excel_file = FileField('Excel File', validators=[DataRequired()])
    submit = SubmitField('Upload')

class FilterForm(FlaskForm):
    phase = SelectField('Excavation Phase', choices=[], validators=[DataRequired()])
    submit = SubmitField('Filter')