from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, check_endpoint_info

import mariadb
import dbcreds

app = Flask(__name__)

app.run(debug=True)

