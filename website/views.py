from flask import  Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import json

views = Blueprint('views', __name__)


