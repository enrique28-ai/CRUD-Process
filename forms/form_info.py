from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField
from wtforms.validators import Length, NumberRange, InputRequired

class ProcessForm(FlaskForm):
    name = StringField(label='Process Name ', validators=[Length(min=2, max=30), InputRequired()])
    duration = DecimalField(label='Duration ', validators=[NumberRange(min=0), InputRequired()])
    operators = IntegerField(label='Number of Operators ', validators=[NumberRange(min=0), InputRequired()])
    cycle_time = DecimalField("Standard Cycle Time (Seconds)", validators=[NumberRange(min=0), InputRequired()])
    units_produced = IntegerField("Units Produced", validators=[NumberRange(min=0), InputRequired()])
    setup_time = DecimalField("Setup Time (Seconds)", validators=[NumberRange(min=0), InputRequired()])
    downtime = DecimalField("Downtime (Seconds)", validators=[NumberRange(min=0), InputRequired()])
    submit = SubmitField(label='Save')
