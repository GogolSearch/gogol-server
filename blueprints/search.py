import html
import time

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
    # Start time for measuring the delta
    start_time = time.time()

    q = request.args.get('q')
    cleaned_query = html.escape(q)
    if not q:
        return redirect(url_for('search.main'))

    items_per_page = current_app.config["web_items_per_page"]
    start = request.args.get('start', 0, type=int)

    if start < 0:
        start = 0

    repo = current_app.config["query_repository"]
    results = repo.search(cleaned_query, start, items_per_page)
    # Calculate the delta in milliseconds
    end_time = time.time()
    delta = (end_time - start_time) * 1000  # Convert seconds to milliseconds
    total_results = results[0]["total_results"] if len(results) > 0 else 0
    return render_template(
        "search/search.html",
        results=results,
        cleaned_query=cleaned_query,
        delta=round(delta),
        total_results=total_results,
        start=start,
        limit=items_per_page,
    )


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