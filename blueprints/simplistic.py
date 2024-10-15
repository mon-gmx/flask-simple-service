from flask import Blueprint, jsonify, request
from flask import current_app
from prometheus_client import Counter, Histogram, generate_latest
from uuid import uuid4
from utils import get_now_time
from models import RequestLog
import random
import logging

# Define the blueprint
simplistic_bp = Blueprint('simplistic', __name__)

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total Request Count', ['endpoint', 'method'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])


@simplistic_bp.route('/data', methods=['GET', 'POST'])
def data():
    logger.debug(f"Received {request.method} request on /data")
    if request.method == 'GET':
        return jsonify({'random_number': uuid4()})
    elif request.method == 'POST':
        return jsonify(request.get_json())

@simplistic_bp.route('/error', methods=['GET'])
def error():
    errors = [400, 401, 404, 419, 429, 500, 503]
    return '', random.choice(errors)

@simplistic_bp.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200

@simplistic_bp.before_request
def start_timer():
    request.start_time = get_now_time()

@simplistic_bp.after_request
def log_request(response):
    latency = (get_now_time() - request.start_time).total_seconds()
    REQUEST_LATENCY.labels(request.endpoint).observe(latency)
    REQUEST_COUNT.labels(request.endpoint, request.method).inc()

    # Log the request
    log_data = RequestLog(
        ip_address=request.remote_addr,
        endpoint=request.path,
        method=request.method,
        response_code=response.status_code,
        timestamp=get_now_time()
    )
    current_app.db.session.add(log_data)
    current_app.db.session.commit()

    return response
