"""The App Initiation file.

This module is for the initiation of the flask app.
"""

import os
from http import HTTPStatus

import secure
from flask import Flask, current_app, g, request
from flask_cors import CORS
from flask_jwt_oidc.exceptions import AuthError

from condition_api.auth import jwt
from condition_api.config import get_named_config
from condition_api.models import db, ma, migrate
from condition_api.utils.cache import cache
from condition_api.utils.util import allowedorigins


# Security Response headers
csp = (
    secure.ContentSecurityPolicy()
    .default_src("'self'")
    # No 'unsafe-inline' for scripts: the API serves JSON (and user-influenced
    # strings consumed by the web app), so inline-script execution should never
    # be permitted. (Note: this disables the inline init of the flask-restx
    # Swagger UI page where CSP is enforced; the API itself is unaffected.)
    .script_src("'self'")
    .style_src("'self' 'unsafe-inline'")
    .img_src("'self' data:")
    .object_src("'self'")
    .connect_src("'self'")
)

hsts = secure.StrictTransportSecurity().include_subdomains().preload().max_age(31536000)
referrer = secure.ReferrerPolicy().no_referrer()
cache_value = secure.CacheControl().no_store().max_age(0)
xfo_value = secure.XFrameOptions().deny()
secure_headers = secure.Secure(
    csp=csp,
    hsts=hsts,
    referrer=referrer,
    cache=cache_value,
    xfo=xfo_value
)


def create_app(run_mode=os.getenv('FLASK_ENV', 'development')):
    """Create flask app."""
    from condition_api.resources import API_BLUEPRINT, OPS_BLUEPRINT  # pylint: disable=import-outside-toplevel

    # Flask app initialize
    app = Flask(__name__)

    # All configuration are in config file
    app.config.from_object(get_named_config(run_mode))

    CORS(app, origins=allowedorigins(), supports_credentials=True)

    # Register blueprints
    app.register_blueprint(API_BLUEPRINT)
    app.register_blueprint(OPS_BLUEPRINT)

    # Setup jwt for keycloak
    if os.getenv('FLASK_ENV', 'production') != 'testing':
        setup_jwt_manager(app, jwt)

    # Database connection initialize
    db.init_app(app)

    # Database migrate initialize
    migrate.init_app(app, db)

    # Marshmallow initialize
    ma.init_app(app)

    @app.before_request
    def set_origin():
        g.origin_url = request.environ.get('HTTP_ORIGIN', 'localhost')
        auth_header = request.headers.get('Authorization', None)
        if auth_header and auth_header.startswith('Bearer '):
            g.access_token = auth_header.split(' ')[1]
        else:
            g.access_token = None

    build_cache(app)

    @app.after_request
    def set_secure_headers(response):
        """Set CORS headers for security."""
        secure_headers.framework.flask(response)
        response.headers.add('Cross-Origin-Resource-Policy', '*')
        response.headers['Cross-Origin-Opener-Policy'] = '*'
        response.headers['Cross-Origin-Embedder-Policy'] = 'unsafe-none'
        return response

    @app.errorhandler(AuthError)
    def handle_auth_error(err):
        """Map authentication/authorization failures to their HTTP status.

        Without this, an invalid/missing token raised by the auth layer falls
        through to the generic Exception handler and surfaces as 500, masking
        genuine 401/403 auth failures from monitoring.
        """
        status_code = getattr(err, "status_code", HTTPStatus.UNAUTHORIZED)
        current_app.logger.info("Auth failure (%s): %s", status_code, getattr(err, "error", err))
        body = getattr(err, "error", None) or {"message": "Unauthorized"}
        return body, status_code

    @app.errorhandler(Exception)
    def handle_error(err):
        if run_mode != "production":
            # To get stacktrace in local development for internal server errors
            raise err
        current_app.logger.error(str(err))
        return "Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR

    # Return App for run in run.py file
    return app


def build_cache(app):
    """Build cache."""
    cache.init_app(app)


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""

    def get_roles(a_dict):
        realm_access = a_dict.get('realm_access', {})
        realm_roles = realm_access.get('roles', [])

        client_name = current_app.config.get('JWT_OIDC_AUDIENCE')

        resource_access = a_dict.get('resource_access', {})
        client_roles = resource_access.get(client_name, {}).get('roles', [])

        return realm_roles + client_roles

    app.config['JWT_ROLE_CALLBACK'] = get_roles

    jwt_manager.init_app(app)
