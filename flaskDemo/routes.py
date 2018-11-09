import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import AddEmployeeForm, RemoveEmployeeForm
from flaskDemo.models import Department, Employee, Project, Works_On


@app.route("/")
@app.route("/home")
def home():
    results = Project.query.join(Works_On,Works_On.pno == Project.pnumber).join(Employee,Employee.ssn == Works_On.essn) \
              .add_columns(Works_On.essn, Project.pnumber, Project.pname, Employee.fname, Employee.lname).all()
    projects = {}
    for row in results:
    	if (str(row.pnumber) + ' ' + row.pname) in projects:
    	    projects[(str(row.pnumber) + ' ' + row.pname)].append([row.fname, row.lname, row.essn])
    	else:
    		projects[(str(row.pnumber) + ' ' + row.pname)] = [[row.fname, row.lname, row.essn]]
    return render_template('home.html', title='Home', projects=projects)


@app.route("/project/<pnumber>")
def project(pnumber):
    project = Project.query.get_or_404(pnumber)
    results = Project.query.join(Works_On,Works_On.pno == Project.pnumber).join(Employee,Employee.ssn == Works_On.essn) \
              .add_columns(Works_On.essn, Project.pnumber, Project.pname, Employee.fname, Employee.lname).filter(Project.pnumber == pnumber)
    return render_template('project.html', results=results, project=project)


@app.route("/project/<pnumber>/remove", methods=['GET', 'POST'])
def remove_employee(pnumber):
    project = Project.query.get_or_404(pnumber)
    results = Project.query.join(Works_On,Works_On.pno == Project.pnumber).join(Employee,Employee.ssn == Works_On.essn) \
              .add_columns(Works_On.essn, Project.pnumber, Employee.fname, Employee.lname).filter(Project.pnumber == pnumber)
    form = RemoveEmployeeForm()
    if form.validate_on_submit():
        works_on = Works_On.query.get((form.employee.data, pnumber))
        try:
            db.session.delete(works_on)
            db.session.commit()
            flash('This employee has been removed from this project!', 'success')
        except:
            flash('This employee is not assigned to this project!', 'error')
        return redirect(url_for('project', pnumber=pnumber))
    return render_template('remove_employee.html', title='Remove Employee',
                           form=form, legend='Remove Employee from Project', results=results, project=project)

@app.route("/project/<pnumber>/add", methods=['GET', 'POST'])
def add_employee(pnumber):
    project = Project.query.get_or_404(pnumber)
    results = Project.query.join(Works_On,Works_On.pno == Project.pnumber).join(Employee,Employee.ssn == Works_On.essn) \
              .add_columns(Works_On.essn, Project.pnumber, Employee.fname, Employee.lname).filter(Project.pnumber == pnumber)
    form = AddEmployeeForm()
    if form.validate_on_submit():
        works_on = Works_On(essn=form.employee.data, pno=pnumber, hours=str(form.hours.data))
        try:
            db.session.add(works_on)
            db.session.commit()
            flash('This employee has been added to this project with ' + str(form.hours.data) + ' hours!', 'success')
        except:
        	flash('This employee is already working on this project!', 'error')
        return redirect(url_for('project', pnumber=pnumber))
    return render_template('add_employee.html', title='Add Employee',
                           form=form, legend='Add Employee to Project', results=results, project=project)