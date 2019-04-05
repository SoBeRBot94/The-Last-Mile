#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(25))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(25))
    password = db.Column(db.String(80))

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(25))
    volume = db.Column(db.Integer)
    vendorName = db.Column(db.String(25))
    inception = db.Column(db.String(25))
    intermediate = db.Column(db.Boolean)
    interDestWarehouse = db.Column(db.String(25))
    pickupTime = db.Column(db.DateTime(timezone=False))
    mappedEmployeeID = db.Column(db.String(25), unique=True)
    packageStatus = db.Column(db.String(10))
    dropTime = db.Column(db.DateTime(timezone=False))
    packageCurrentLocation = db.Column(db.String(25))

def employeeToken(f):
    @wraps(f)
    def decoratedFunction(*args, **kargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'Message' : 'Token is Missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            currentEmployee = Employee.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'Message' : 'Token is Invalid!'}), 401

        return f(currentEmployee, *args, **kargs)

    return decoratedFunction

@app.route('/employee', methods=['GET'])
@employeeToken
def get_employee_list(currentEmployee):
    
    if not currentEmployee.admin:
        return jsonify({'Message' : 'Cannot Perform Action, You Are Not an Admin!'})
    
    employeeList = Employee.query.all()

    output = []

    for employee in employeeList:
        employeeData = {}
        employeeData['public_id'] = employee.public_id
        employeeData['name'] = employee.name
        employeeData['password'] = employee.password
        employeeData['admin'] = employee.admin
        output.append(employeeData)

    return jsonify({'Employees': output})

@app.route('/employee/<public_id>', methods=['GET'])
@employeeToken
def get_employee(currentEmployee, public_id):
    
    if not currentEmployee.admin:
        return jsonify({'Message' : 'Cannot Perform Action, You Are Not an Admin!'})
    
    employee = Employee.query.filter_by(public_id=public_id).first()

    if not employee:
        return jsonify({'Message' : 'No Employee Found!' })

    employeeData = {}
    employeeData['public_id'] = employee.public_id
    employeeData['name'] = employee.name
    employeeData['password'] = employee.password
    employeeData['admin'] = employee.admin
    
    return jsonify({'Employee' : employeeData})

@app.route('/employee', methods=['POST'])
@employeeToken
def create_employee(currentEmployee):
    employeeData = request.get_json()

    hashedPassword = generate_password_hash(employeeData['password'], method='sha256')

    newEmployee = Employee(public_id=str(uuid.uuid4()), name=employeeData['name'], password=hashedPassword, admin=False)

    db.session.add(newEmployee)
    db.session.commit()

    return jsonify({'Message' : 'New Employee has been created!'})

@app.route('/employee/<public_id>', methods=['PUT'])
@employeeToken
def promote_employee(currentEmployee, public_id):
    
    if not currentEmployee.admin:
        return jsonify({'Message' : 'Cannot Perform Action, You Are Not an Admin!'})
    
    employee = Employee.query.filter_by(public_id=public_id).first()

    if not employee:
        return jsonify({'Message': 'No Employee Found to Promote!'})

    employee.admin=True

    db.session.commit()

    return jsonify({'Message' : 'The Employee has been Promoted to Admin!'})

@app.route('/employee/<public_id>', methods=['DELETE'])
@employeeToken
def delete_employee(currentEmployee, public_id):
    employee = Employee.query.filter_by(public_id=public_id).first()

    if not employee:
        return jsonify({'Message': 'No Employee Found to Remove!'})

    db.session.delete(employee)
    db.session.commit()

    return jsonify({'Message': 'Employee \t' + employee.name + '\t has been Removed!'})

@app.route('/employeelogin', methods=['GET'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})

    employee = Employee.query.filter_by(name=auth.username).first()

    if not employee:
        return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})

    if check_password_hash(employee.password, auth.password):
        token = jwt.encode({'public_id' : employee.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})
    
    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})


if __name__ == '__main__':
    app.run()
