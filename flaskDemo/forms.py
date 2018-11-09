from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import Department, Employee, Project, Works_On
from wtforms.fields.html5 import DateField

employee = Employee.query.with_entities(Employee.ssn, Employee.fname, Employee.lname).distinct()
print(employee)
e_choices = [(row[0],row[1] + ' ' + row[2]) for row in employee]

projects = Project.query.with_entities(Project.pnumber).distinct()
p_choices = [(row[0],row[0]) for row in projects]

class AddEmployeeForm(FlaskForm):
    employee = SelectField("Employee", choices=e_choices)
    submit = SubmitField('Add Employee to Project')
    hours = IntegerField('Add Hours Worked')

class RemoveEmployeeForm(FlaskForm):
    employee = SelectField("Employee", choices=e_choices)
    submit = SubmitField('Remove Employee from Project')