import requests
from .helper import IntegrationHelperService
from typing import TYPE_CHECKING
from .approval import ISApprovalClient
from .auth import AuthIntegrationService
import traceback

if TYPE_CHECKING:
    from ...models.approval_step import ApprovalStep
    from ...models.res_users import ResUsers


class ISApprovalStepClient:
    def __init__(self, env):
        self.env = env

        self.org_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("vnfield_cs.organization_name")
        )

        self.base_url = (
            self.env["ir.config_parameter"].sudo().get_param("vnfield_cs.host_of_is")
            + "/send_request?model=vnfield.approval.step"
        )

        self.auth_service = AuthIntegrationService(env)

    def update(self, vals: dict, approval_step: "ApprovalStep", user: "ResUsers"):
        try:
            body = {"fields": list(vals.keys()), "values": vals}
            if approval_step["external_id"]:
                url = self.base_url + "&Id=" + str(approval_step["external_id"])
                headers = {
                    "Content-Type": "application/json",
                    "login": user.external_login,
                    "password": user.external_password,
                    "api-key": self.auth_service.get_api_key(user),
                }
                print(body)
                requests.put(url, json=body, headers=headers)
        except Exception as e:
            traceback.print_exc()

    def create(self, vals: dict, approval_step: "ApprovalStep", user: "ResUsers"):
        try:
            body = {"fields": list(vals.keys()), "values": vals}
            url = self.base_url
            headers = {
                "Content-Type": "application/json",
                "login": user.external_login,
                "password": user.external_password,
                "api-key": self.auth_service.get_api_key(user),
            }
            print(headers)
            response = requests.post(url, json=body, headers=headers)
            print("Approval create res: ", body)
            response_json = response.json()

            return {"external_id": response_json["New resource"][0]["id"]}
        except Exception as e:
            traceback.print_exc()


class ApprovalStepIntegrationService:

    def __init__(self, env):
        self.env = env

        self.helper = IntegrationHelperService(self.env)

        self.approval_client = ISApprovalClient(self.env)
        self.approval_step_client = ISApprovalStepClient(self.env)

    def update(self, vals: dict, approval_step: "ApprovalStep", user: "ResUsers"):

        if approval_step.approver_id and not self.helper.user_is_internal(
            approval_step.approver_id
        ):
            if not approval_step["external_id"]:
                if approval_step.approval_id.id:
                    approval_data = approval_step.approval_id.to_dict()
                    response = self.approval_client.create(approval_data, user)
                    approval_step.approval_id.write(
                        {"external_id": response["external_id"]}
                    )
                approval_step_data = approval_step.to_dict()
                approval_step_data["approver_id"] = (
                    approval_step.approver_id.external_id
                )
                response = self.approval_step_client.create(
                    approval_step_data, approval_step, user
                )
                print("@Update response: ", response)
                approval_step.write({"external_id": response["external_id"]})
            else:
                self.approval_step_client.update(vals, approval_step, user)

    def create(self, approval_step: "ApprovalStep", user: "ResUsers"):

        if approval_step.approver_id.id and not self.helper.user_is_internal(
            approval_step.approver_id
        ):
            if approval_step.approval_id.id:
                approval_data = approval_step.approval_id.to_dict()
                approval_data["requester_id"] = (
                    approval_step.approval_id.requester_id.external_id
                )
                response = self.approval_client.create(
                    approval_data, approval_step, user
                )
                approval_step.approval_id.write(
                    {"external_id": response["external_id"]}
                )
            approval_step_data = approval_step.to_dict()
            approval_step_data["approver_id"] = approval_step.approver_id.external_id
            response = self.approval_step_client.create(
                approval_step_data, approval_step, user
            )
            approval_step.write({"external_id": response["external_id"]})
