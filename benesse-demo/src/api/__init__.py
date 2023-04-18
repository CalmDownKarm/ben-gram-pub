from flask import Blueprint, jsonify

api = Blueprint('routes', __name__)

from .corrections import *
from .model.interactive_copy import *
