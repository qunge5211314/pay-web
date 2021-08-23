from manager import app
from micro_service_authorization import AuthorizationTool


with app.app_context():
    AUTH = AuthorizationTool(app, "daka_pay").get_auth_authorization()