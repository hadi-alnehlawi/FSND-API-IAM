import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()
# insert sample data
drink = Drink(
    title='water',
    recipe='[{"name": "water", "color": "blue", "parts": 1}]'
)
drink.insert()
# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drinks_list = [drink.short() for drink in Drink.query.all()]
    if not drinks:
        abort(404)
    else:
        return jsonify({"success": True, "drinks": drinks_list})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    drinks_list = [drink.short() for drink in drinks]
    if not drinks:
        abort(404)
    else:
        return jsonify({"success": True, "drinks": drinks_list}), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    if not body:
        abort(404)
    else:
        try:
            title = body.get('title')
            recipe = body.get('recipe')
            new_drink = Drink(title=title, recipe=json.dumps(recipe))
            new_drink.insert()
            return jsonify({"success": True, "drinks": new_drink.long()}), 200
        except:
            abort(405)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@ app.route('/drinks/<int:id>', methods=['PATCH'])
@ requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    else:
        try:
            body = request.get_json()
            title = body.get('title')
            # convert json to string
            recipe = json.dumps(body.get('recipe'))
            drink.title = title
            drink.recipe = recipe
            drink.update()
            return jsonify({"success": True, "drinks": drink.long()}), 200
        except:
            abort(405)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@ app.route('/drinks/<int:id>', methods=['DELETE'])
@ requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    else:
        try:
            drink.delete()
            return jsonify({"success": True, "delete": id})
        except:
            abort(405)


'''
Example error handling for unprocessable entity
'''


@ app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Not Acceptable"
    }), 405


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@ app.errorhandler(404)
def error_handler_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@ app.errorhandler(401)
def authentication_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'unauthorized'
    }), 401
