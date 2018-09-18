from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
#TODO: probably want to restrict where requests come from
CORS(app)

from app import routes
