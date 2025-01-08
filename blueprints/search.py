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
    if not q:
        return redirect(url_for('search.main'))

    items_per_page = current_app.config["web_items_per_page"]
    page = request.args.get('page', 1, type=int)

    if page < 1:
        page = 1

    safe_search = request.cookies.get("safeSearch", False)
    try:
        if not isinstance(safe_search, bool):
            safe_search = utils.converters.str_to_bool(safe_search)
    except ValueError:
        safe_search = False

    repo = current_app.config["query_repository"]
    results = repo.search(q, page, items_per_page, safe_search)
    # Calculate the delta in milliseconds
    end_time = time.time()
    delta = (end_time - start_time) * 1000  # Convert seconds to milliseconds
    total_results = results[0]["total_results"] if len(results) > 0 else 0

    return render_template(
        "search/search.html",
        results=results,
        cleaned_query=html.escape(q),
        delta=round(delta),
        total_results=total_results,
        current_page=page,
        min_page=1,
        max_page=round(total_results / items_per_page),
        q=q,
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