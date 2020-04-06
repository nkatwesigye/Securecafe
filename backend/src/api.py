import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

'''
!! NOTE :Add drinks to drinks table 
!! NOTE: List of drinks
!! NOTE: Update list of drinks to add drinks or uncomment 
'''
# drink_list=[{
#    "title": "Water5",
#    "recipe": [{
#        "name": "Water",
#        "color": "pink",
#        "parts": 2
#    }]
# },
# {
#    "title": "Water6",
#    "recipe": [{
#        "name": "Water",
#        "color": "red",
#        "parts": 3
#    }]
# }]


## initialize for a fresh database table 
def create_drinks(drink_list):
    for drinks in drink_list: 
        drink = Drink(title = drinks['title'], recipe=json.dumps(drinks['recipe']))
        drink.insert()

## Get drink in long format
def get_long_drinks():
    drinks=[]
    get_drinks = Drink.query.all()
    for drink in get_drinks:
        drinks.append(drink.long())
    return drinks

## Get drink in short format without recipes
def get_short_drinks():
    drinks=[]
    get_drinks = Drink.query.all()
    for drink in get_drinks:
        drinks.append(drink.short())
    return drinks


'''
!! NOTE: Only uncomment to intialize new drinks for a clean table without using the api
'''
#create_drinks(drink_list)


## ROUTES

## Get all drinks without recipe(short_format)
@app.route('/drinks')
def get_drinks():
    drinks = get_short_drinks()
    return jsonify({
     'success': True,
     'drinks' : drinks

    })

## Get all drinks with recipe(long_format)
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = get_long_drinks()
    return jsonify({
       'success': True,
       'drinks' : drinks
    })

## Add a new drink 
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
    new_drink_params = request.json
    title = new_drink_params['title']
    recipe = new_drink_params['recipe']
    drink = Drink(title = title, recipe=json.dumps(recipe))
    drink.insert()
    drinks = get_long_drinks()   
    return jsonify({
         'success': True,
         'drinks': drinks

    })

## Update existing drink using drink id
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(payload,drink_id):
  drink = []
  drink_by_id = Drink.query.filter_by(id=drink_id).first()
  if drink_by_id is None :
        abort(404)
  updated_drink_param = request.json
  print(updated_drink_param)
  try:
   update_title = updated_drink_param['title']
   update_recipe = updated_drink_param['recipe']
   drink_by_id.title = update_title
   drink_by_id.recipe = json.dumps(update_recipe) 
   drink_by_id.update()
  except KeyError:
    abort(404)
  drink_by_id.title = update_title
  drink_by_id.recipe = json.dumps(update_recipe) 
  drink_by_id.update()
  get_updated_drink = Drink.query.filter_by(id=drink_id)
  for updated_drink in get_updated_drink:
     drink.append(updated_drink.long())
  return jsonify({
      'success': True,
      'drinks': drink
    })
    


## Delete a drink from list of drinks based on drink id
@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(payload,drink_id):
  drink_by_id = Drink.query.filter_by(id=drink_id).first()
  if drink_by_id is None :
        abort(404)
  drink_by_id.delete()
  return jsonify({
      'success': True,
      'deleted': drink_id
    })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": " resource not found"
                    }), 404

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": " Un Authorized"
                    }), 401

