from ...models.res_users import ResUsers


class IntegrationHelperService:

    def __init__(self, env):
        self.env = env
        self.org_config = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("vnfield_cs.organization_name")
        )

    def user_is_internal(self, requester: ResUsers):
        """
        requester: bản ghi res.users
        Kiểm tra xem requester có thuộc tổ chức được config không.
        """
        print("@User is internal: ", self.org_config)
        if requester.organization_name != self.org_config:
            return False
        # Nếu qua kiểm tra, làm tiếp công việc khác
        return True
