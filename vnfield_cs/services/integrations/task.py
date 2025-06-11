import requests
from .helper import IntegrationHelperService
from typing import TYPE_CHECKING
from .auth import AuthIntegrationService
import traceback

if TYPE_CHECKING:
    from ...models.task import Task
    from ...models.res_users import ResUsers


class ISTaskClient:
    def __init__(self, env):
        self.env = env

        self.org_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("vnfield_cs.organization_name")
        )

        self.base_url = (
            self.env["ir.config_parameter"].sudo().get_param("vnfield_cs.host_of_is")
            + "/send_request?model=vnfield.task"
        )

        self.auth_service = AuthIntegrationService(env)

    def update(self, vals: dict, task: "Task", user: "ResUsers"):
        try:
            body = {"fields": list(vals.keys()), "values": vals}
            if task["external_id"]:
                url = self.base_url + "&Id=" + str(task["external_id"])
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

    def create(self, vals: dict, task: "Task", user: "ResUsers"):
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
            print("Task create res: ", body)
            response_json = response.json()

            return {"external_id": response_json["New resource"][0]["id"]}
        except Exception as e:
            traceback.print_exc()


class TaskIntegrationService:

    def __init__(self, env):
        self.env = env

        self.helper = IntegrationHelperService(self.env)

        self.task_client = ISTaskClient(self.env)

    def update(self, vals: dict, task: "Task", user: "ResUsers"):
        if (
            (task.assignee_id and not self.helper.user_is_internal(task.assignee_id))
            or (task.verifier_id and not self.helper.user_is_internal(task.verifier_id))
            or (task.assigner_id and not self.helper.user_is_internal(task.assigner_id))
        ):
            task_data = task.to_dict()
            if "assignee_id" in vals and (
                task.assignee_id and not self.helper.user_is_internal(task.assignee_id)
            ):
                task_data["assignee_id"] = task.assignee_id.external_id
            if "assigner_id" in vals and (
                task.assigner_id and not self.helper.user_is_internal(task.assigner_id)
            ):
                task_data["assigner_id"] = task.assigner_id.external_id
            if "verifier_id" in vals and (
                task.verifier_id and not self.helper.user_is_internal(task.verifier_id)
            ):
                task_data["verifier_id"] = task.verifier_id.external_id

            if not task["external_id"]:

                response = self.task_client.create(task_data, task, user)
                print("@Update response: ", response)
                task.write({"external_id": response["external_id"]})
            else:
                self.task_client.update(vals, task, user)

    def create(self, task: "Task", user: "ResUsers"):

        if task.approver_id.id and not self.helper.user_is_internal(task.approver_id):
            if task.approval_id.id:
                approval_data = task.approval_id.to_dict()
                approval_data["requester_id"] = (
                    task.approval_id.requester_id.external_id
                )
                response = self.approval_client.create(approval_data, task, user)
                task.approval_id.write({"external_id": response["external_id"]})
            task_data = task.to_dict()
            task_data["approver_id"] = task.approver_id.external_id
            response = self.task_client.create(task_data, task, user)
            task.write({"external_id": response["external_id"]})
