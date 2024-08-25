from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, check_endpoint_info, new_token

import mariadb
import dbcreds

app = Flask(__name__)

# Returns information about a single client, will error if the client_id does not exist.
@app.get('/api/user')
def get_client():
    valid_check = check_endpoint_info(request.args, ["client_id"])
    if(type(valid_check) == str):
        return valid_check
    
    id = request.args["client_id"]
    
    try:
        result = run_statement("CALL get_client(?)", [id])
        if (result):
            return make_response(jsonify(result[0]), 200)
        else:
            return make_response("Client not found", 404)
    except Exception as error:
        err = {}
        err["error"] = f"Error calling client: {error}"
        return make_response(jsonify(err), 400)

# Creates a new client that can now use the system. Also returns a valid login token meaning the user is now logged in after sign up.  Will error if there is a duplicate username or password (the user already exists)
@app.post('/api/user')
def create_client():
    valid_check = check_endpoint_info(request.json, 
                                      ["email", "first_name", "last_name", "password"])
    if(type(valid_check) == str):
        return valid_check

    email = request.json["email"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    password = request.json["password"]

    try:
        result = run_statement("CALL create_client(?, ?, ?, ?)", (email, first_name, last_name, password))
        if (result):
            token = new_token()
            # print(token)
            result2 = run_statement("CALL set_token(?,?)", (result[0]['id'], token))
            return make_response(jsonify(result2[0]), 201)
            # return make_response(jsonify([result[0], {"token": token}]), 200)

    except Exception as error:
        err = {}
        err["error"] = f"Error creating client: {error}"
        return make_response(jsonify(err), 400)


# Modify an existing user if you have a valid token. Note that the token is sent as a header.
@app.patch('/api/user')
def update_client():
   
    valid_check = check_endpoint_info(request.headers, ["token"])
    if(type(valid_check) == str):
        return valid_check
    
    email = first_name = last_name = password = ""

    if(request.json.get("email") is not None):
        email = request.json["email"]
    if(request.json.get("first_name") is not None):
        first_name = request.json["first_name"]
    if(request.json.get("last_name") is not None):
        last_name = request.json["last_name"]
    if(request.json.get("password") is not None):
        password = request.json["password"]
        
    token = request.headers["token"]

    try:
        run_statement("CALL update_client(?, ?, ?, ?, ?,)", (email, first_name, last_name, password, token))
        return make_response('',201)
    except Exception as error:
        err = {}
        err["error"] = f"Error updating client: {error}"
        return make_response(jsonify(err), 400)


# Delete an existing user if you have a valid token and password. Note that the token is sent as a header.
@app.delete('/api/user')
def delete_client():
    valid_check = check_endpoint_info(request.headers,  ["token"])
    if(type(valid_check) == str):
        return valid_check
    
    password = request.json["password"]
    token = request.headers["token"]
    try:
        result = run_statement("CALL delete_client(?, ?)", (password, token))
        if (result[0]["message"] == "Success"):
            return make_response('', 201)
        else:
            err = {}
            err["error"] = f"Error deleting client: {result[0]["message"]}"
            return make_response(jsonify(err), 400)
    except Exception as error:
        err = {}
        err["error"] = f"Error deleting client: {error}"
        return make_response(jsonify(err), 400)

# Log a client in. Will error if the email / password don't exist in the system.
@app.post('/api/login')
def client_login():
    valid_check = check_endpoint_info(request.json, ["email", "password"])
    if(type(valid_check) == str):
        return valid_check

    email = request.json["email"]
    password = request.json["password"]

    # add password hashing here
    # add email authentication here

    try:
        result = run_statement("CALL client_login(?, ?)", (email, password))
        if (result):
            token = new_token()
            result2 = run_statement("CALL set_token(?,?)", (result[0]['id'], token))
            return make_response(jsonify(result2[0]), 200)
    except Exception as error:
        err = {}
        err["error"] = f"Error logging in client: {error}"
        return make_response(jsonify(err), 400)

# Delete an existing token. Will error if the token sent does not exist.
@app.delete('/api/login')
def client_logout():
    valid_check = check_endpoint_info(request.headers,  ["token"])
    if(type(valid_check) == str):
        return valid_check
    
    token = request.headers["token"]
    try:
        result = run_statement("CALL client_logout(?)", [token])
        if (result):
            return make_response('', 200)
    except Exception as error:
        err = {}
        err["error"] = f"Error logging out client: {error}"
        return make_response(jsonify(err), 400)

app.run(debug=True)

