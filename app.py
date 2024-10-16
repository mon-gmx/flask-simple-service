import logging
import logging.config

import yaml
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from prometheus_client import CollectorRegistry

from blueprints.simplistic import simplistic_bp
from config import DevelopmentConfig, TestConfig
from models import RequestLog


def create_app(config_class=DevelopmentConfig):
    with open("logging.yaml", "r") as f:
        logging_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logging_config)
    app = Flask(__name__)
    app.db = SQLAlchemy()
    app.config.from_object(config_class)
    registry = CollectorRegistry()

    # Initialize the database
    app.db.init_app(app)

    # Register the blueprint
    app.register_blueprint(simplistic_bp)

    with app.app_context():

        resource = Resource.create({"service.name": "simple_service"})

        # Set up tracing
        trace.set_tracer_provider(TracerProvider(resource=resource))
        jaeger_config = app.config.get("JAEGER_SETTINGS")
        if jaeger_config:
            if jaeger_config.get("enabled", False):
                jaeger_exporter = JaegerExporter(
                    agent_host_name=jaeger_config.get("host"),  # Change this to your Jaeger agent host
                    agent_port=jaeger_config.get("port"),
                )
                trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(jaeger_exporter))
        # Instrument the Flask app
        FlaskInstrumentor().instrument_app(app)
        # Instrument SQLAlchemy with the app context
        SQLAlchemyInstrumentor().instrument(engine=app.db.engine)

    return app
