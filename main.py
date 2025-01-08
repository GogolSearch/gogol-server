import argparse
import atexit
import logging
import os
import signal
import sys
from typing import Any

import psycopg_pool
import redis
from flask import Flask, g
from blueprints.search import bp as search_bp
from implementations.backend import PostgreSQLBackend
from implementations.cache import RedisCache
from implementations.repository import QueryRepository

def get_env_variable(name, default=None) -> Any:
    """Helper to fetch environment variables with optional defaults."""
    return os.environ.get(name, default)

def configure_logging(log_level) -> None:
    """Configure logging for the application."""
    levels = logging.getLevelNamesMapping()
    logging.basicConfig(level=levels.get(log_level, logging.INFO), stream=sys.stdout)

def create_connection_pool(config) -> psycopg_pool.ConnectionPool:
    """Create and return a connection pool."""
    return psycopg_pool.ConnectionPool(
            min_size=1,
            max_size=3,
            conninfo=f"dbname={config['db_name']} user={config['db_user']} password={config['db_password']} "
                     f"host={config['db_host']} port={config['db_port']}"
    )



def create_redis_client(config) -> redis.Redis:
    """Create and return a Redis client."""
    return redis.Redis(
        host=config["redis_host"],
        port=config["redis_port"],
        db=config["redis_db"],
        encoding="utf-8",
        decode_responses=True
    )

def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description='Crawler configuration')

    # Database arguments
    parser.add_argument(
        '--db_host',
        type=str,
        default=get_env_variable('DB_HOST')
    )

    parser.add_argument(
        '--db_name',
        type=str,
        default=get_env_variable('DB_NAME')
    )

    parser.add_argument(
        '--db_user',
        type=str,
        default=get_env_variable('DB_USER')
    )

    parser.add_argument(
        '--db_password',
        type=str,
        default=get_env_variable('DB_PASSWORD')
    )

    parser.add_argument(
        '--db_port',
        type=int,
        default=get_env_variable('DB_PORT')
    )

    # Redis arguments
    parser.add_argument(
        '--redis_host',
        type=str,
        default=get_env_variable('REDIS_HOST')
    )

    parser.add_argument(
        '--redis_port',
        type=int,
        default=get_env_variable('REDIS_PORT')
    )

    parser.add_argument(
        '--redis_db',
        type=int,
        default=get_env_variable('REDIS_DB', default=0)
    )

    # Crawler configuration
    parser.add_argument(
        "--log_level",
        type=str,
        default=get_env_variable('LOG_LEVEL', default="INFO")
    )

    parser.add_argument(
        "--cache_queries_list_key",
        type=str,
        default=get_env_variable('CACHE_QUERIES_LIST_KEY', default="queries_list")
    )
    parser.add_argument(
        "--web_items_per_page",
        type=int,
        default=get_env_variable('WEb_ITEMS_PER_PAGE', default=10)
    )
    # Parse and return the arguments
    return parser.parse_args()

def create_app():
    args = parse_args()
    config = vars(args)  # Convert Namespace to dict

    for k, v in config.items():
        if v is None:
            raise ValueError(f"key: {k} is required")

    # Configure logging
    configure_logging(config["log_level"])

    # Initialize global resources
    pool = create_connection_pool(config)
    redis_client = create_redis_client(config)

    backend = PostgreSQLBackend(pool)
    cache = RedisCache(redis_client, config["cache_queries_list_key"])
    query_repository = QueryRepository(cache, backend)

    app = Flask(__name__, static_url_path='/static', static_folder='static')

    for k, v in config.items():
        app.config[k] = v

    app.config["query_repository"] = query_repository

    def on_shutdown():
        pool.close()
        redis_client.close()

    atexit.register(on_shutdown)

    # Register blueprints
    app.register_blueprint(search_bp)

    return app

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == '__main__':
    main()
