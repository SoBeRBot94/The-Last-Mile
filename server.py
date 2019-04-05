#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import requests


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

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qr_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(25))
    volume = db.Column(db.Integer)
    vendorName = db.Column(db.String(25))
    inception = db.Column(db.String(25))
    intraCityDelivery = db.Column(db.Boolean)
    deliveryLocation = db.Column(db.String(50))
    pickupTime = db.Column(db.DateTime(timezone=False))
    packageStatus = db.Column(db.String(10))
    dropTime = db.Column(db.DateTime(timezone=False))
    packageCurrentLocation = db.Column(db.String(25))

# Employee

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
def employeeLogin():
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

# Vendor

def vendorToken(f):
    @wraps(f)
    def decoratedFunction(*args, **kargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'Message' : 'Token is Missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            currentVendor = Vendor.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'Message' : 'Token is Invalid!'}), 401

        return f(currentVendor, *args, **kargs)

    return decoratedFunction

@app.route('/vendorlogin', methods=['GET'])
def vendorLogin():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})

    vendor = Vendor.query.filter_by(name=auth.username).first()

    if not vendor:
        return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})

    if check_password_hash(vendor.password, auth.password):
        token = jwt.encode({'public_id' : vendor.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})
    
    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required!"'})

@app.route('/vendor', methods=['POST'])
@employeeToken
def create_vendor(currentEmployee):
    
    if not currentEmployee.admin:
        return jsonify({'Message' : 'Cannot Perform Action, You Are Not an Admin!'})
   
    vendorData = request.get_json()

    hashedPassword = generate_password_hash(vendorData['password'], method='sha256')

    newVendor = Vendor(public_id=str(uuid.uuid4()), name=vendorData['name'], password=hashedPassword)

    db.session.add(newVendor)
    db.session.commit()

    return jsonify({'Message' : 'New Vendor has been created!'})

# Data API

@app.route('/fetchdata', methods=['POST'])
@vendorToken
def fetch_data(currentVendor):

    geoLocateURL = 'https://api.ipgeolocation.io/ipgeo'
    APIKey = 'f38b38d7de524ab2b337dba786fabec0'
    geoLocateData = requests.get(geoLocateURL+'?apiKey='+APIKey+'&fields=city')
    json = geoLocateData.json()
    location = json['city']

    packageData = request.get_json()
    
    newPackage = Package(qr_id=str(uuid.uuid4()), name=packageData['name'],

                         volume=packageData['volume'],

                         vendorName=currentVendor.name,

                         inception=packageData['inception'],

                         intraCityDelivery=packageData['intraCityDelivery'],

                         deliveryLocation=packageData['deliveryLocation'],

                         packageStatus='WAITING',

                         packageCurrentLocation=location)

    db.session.add(newPackage)
    db.session.commit()

    return jsonify({'Message' : 'The Package has been added!'})

@app.route('/fetchdata/<qr_id>', methods=['DELETE'])
@vendorToken
def delete_data(currentVendor, qr_id):

    package = Package.query.filter_by(qr_id=qr_id).first()

    if not package:
        return jsonify({'Message': 'No Package Found to Remove!'})

    db.session.delete(package)
    db.session.commit()

    return jsonify({'Message': 'Package \t' + package.name + '\t has been Removed!'})

    

if __name__ == '__main__':
    app.run()
