from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)
    
class Department(db.Model):
    __table__ = db.Model.metadata.tables['department']
    
class Employee(db.Model):
    __table__ = db.Model.metadata.tables['employee']

class Project(db.Model):
    __table__ = db.Model.metadata.tables['project']
    
class Works_On(db.Model):
    __table__ = db.Model.metadata.tables['works_on']

    

  
