import requests
from typing import TYPE_CHECKING
from odoo.tools import config

if TYPE_CHECKING:
    from ...models.approval import Approval
    from ...models.res_users import ResUsers


class ISAuthClient:
    def __init__(self, env):
        self.env = env

        self.db_name = (
            self.env["ir.config_parameter"].sudo().get_param("vnfield_cs.is_db_name")
        )

        self.base_url = (
            self.env["ir.config_parameter"].sudo().get_param("vnfield_cs.host_of_is")
            + "/odoo_connect"
        )

    def sign_in(self, user: "ResUsers"):
        try:
            url = self.base_url
            headers = {
                "login": user.external_login,
                "password": user.external_password,
                "db": self.db_name,
            }
            print("@Auth: ", url, headers)
            response = requests.get(url, headers=headers)
            return response.json()["api-key"]
        except:
            print("An exception occurred")


class AuthIntegrationService:

    def __init__(self, env):
        self.env = env

        self.auth_client = ISAuthClient(self.env)

    def get_api_key(self, user: "ResUsers"):

        if not user.external_api_key:
            user.write(
                {
                    "external_api_key": self.auth_client.sign_in(user),
                }
            )
        return user.external_api_key
