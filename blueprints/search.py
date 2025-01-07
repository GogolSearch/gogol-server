import functools
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, app, current_app
)

import utils.converters
from utils.converters import str_to_bool

bp = Blueprint('search', __name__, url_prefix='')

@bp.route('/', methods=['GET'])

def main():
    return render_template("search/main.html")

@bp.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    if not q:
        return redirect(url_for('search.main'))

    items_per_page = current_app.config["web_items_per_page"]
    page = request.args.get('page', 1, type=int)

    if page < 1:
        page = 1

    adult = request.cookies.get("adult", False)
    try:
        if not isinstance(adult, bool):
            adult = utils.converters.str_to_bool(adult)
    except ValueError:
        adult = False

    repo = current_app.config["query_repository"]
    results = repo.search(q, page, items_per_page, adult)
    return render_template("search/search.html", results=results)

@bp.route('/api/history', methods=['get'])
def get_history():
    q = request.args.get('q',"")
    n = request.args.get('n', 5, type=int)

    try:
        if n is not None:
            n = int(n)
    except TypeError:
        return jsonify(message="n must be an integer"), 400

    repo = current_app.config["query_repository"]

    return jsonify(data=repo.get_history(q, n))