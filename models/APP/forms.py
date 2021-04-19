from app import *
from etc.config.externalLib import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

class IPForm(FlaskForm):
    ip = StringField('Server IP', validators=[IPAddress(), DataRequired()], render_kw={"placeholder": '192.168.1.1'})
    port = IntegerField('Port', validators=[DataRequired()], render_kw={"placeholder": '80'})
    submit = SubmitField('Connect')

class configNewSession(FlaskForm):
    class Meta:
        def render_field(self, field, render_kw):
            if field.type == "_Option":
                render_kw.setdefault("required", True)
            return super().render_field(field, render_kw)
    session_name = StringField('Session Name', validators=[DataRequired(), Alpha()])
    key_size = RadioField('Key Size', validators=[DataRequired()], choices=[('32','32 Bits'),('64','64 Bits'), ('128','128 Bits'), ('256','256 Bits')])
    data_type = RadioField('Data Type', validators=[DataRequired()], choices=[('Integer', "Integer"), ('Polynomial', 'Polynomial')])
    submit = SubmitField('Create')

class fileForm(FlaskForm):
    file = FileField(validators=[FileRequired()])
    upload = SubmitField('Upload')

class dataEntry_int(FlaskForm):
    def validate_label(form, field):
        if not (field.data.isidentifier()):
            raise ValidationError("Inproper Label. Please follow PEP")
    # Do a validation on requiring str in label
    data_label_int = StringField("Label", validators=[DataRequired(), validate_label], render_kw={'placeholder':'numOfPhone'})
    data_field_int = IntegerField('Data', validators=[DataRequired()], render_kw={"placeholder": '10'})
    submit_int = SubmitField("Submit")

class dataEntry_poly(FlaskForm):
    def validate_label(form, field):
        if not (field.data.isidentifier()):
            raise ValidationError("Inproper Label. Please follow PEP")
    def validate_poly(form, field):
        if not re.match(r"^([+-]?(?:(?:\d+x\^\d+)|(?:\d+x)|(?:\d+)|(?:x)))+$", field.data):
            raise ValidationError('Incorrect form of polynomial (Single-variable)')
    data_label_poly = StringField("Label", validators=[DataRequired(), validate_label], render_kw={'placeholder':'numOfPhone'})
    data_field_poly = StringField('Data',validators=[DataRequired(), validate_poly], render_kw={"placeholder":"2x + 10"})
    submit_poly = SubmitField("Submit")

class dataEval(FlaskForm):
    def validate_label(form, field):
        if not (field.data.isidentifier()):
            raise ValidationError("Inproper Label. Please follow PEP")
    data_label_eval = StringField("Label", validators=[DataRequired(), validate_label], render_kw={'placeholder':'numOfElectronics'})
    data_field_eval = StringField('Expression', validators=[DataRequired()], render_kw={"placeholder": 'numOfPhone + numOfTablet'})
    submit_eval = SubmitField("Submit")

class dataDecrypt(FlaskForm):
    def validate_label(form, field):
        if not (field.data.isidentifier()):
            raise ValidationError("Inproper Label. Please follow PEP")
    data_label_decrypt = StringField("Label", validators=[DataRequired(), validate_label], render_kw={'placeholder':'numOfElectronics'})
    submit_decrypt = SubmitField("Get")

class dataDelete(FlaskForm):
    def validate_label(form, field):
        if not (field.data.isidentifier()):
            raise ValidationError("Inproper Label. Please follow PEP")
    data_label_delete = StringField("Label", validators=[DataRequired(), validate_label], render_kw={'placeholder':'numOfElectronics'})
    submit_delete = SubmitField("Delete")
