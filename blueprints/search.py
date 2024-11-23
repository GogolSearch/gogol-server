import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('search', __name__, url_prefix='')

@bp.route('/', methods=['GET'])

def search():
    return render_template("search/main.html")