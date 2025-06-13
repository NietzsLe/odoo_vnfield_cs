from odoo import api, fields, models, _, exceptions
from odoo.tools.float_utils import float_compare
from ..services.integrations.task import TaskIntegrationService
from datetime import datetime


def serialize_odoo_datetime(value):
    try:
        # Cố gắng chuyển sang datetime; nếu lỗi thì không phải
        isinstance(value, datetime)
    except Exception:
        pass
    return value


class Task(models.Model):
    _inherit = "vnfield.task"
    external_id = fields.Integer()
    changed_by_is = fields.Boolean()

    @api.model
    def create(self, vals):
        # Gán giá trị mặc định hoặc xử lý logic

        record = super(Task, self).create(vals)
        if (not "changed_by_is" in vals) or vals["changed_by_is"] == "no":
            # Hành động sau khi tạo
            integration_service = TaskIntegrationService(self.env)
            integration_service.create(record, self.env.user)
        else:
            self.write({"changed_by_is": "no"})
        return record

    @api.model
    def write(self, vals):
        # Gán giá trị mặc định hoặc xử lý logic

        record = super(Task, self).write(vals)
        if (not "changed_by_is" in vals) or vals["changed_by_is"] == "no":
            if record:
                record = self.env["vnfield.task"].browse(self.id)
                # Hành động sau khi tạo
                print("@Approval step self: ", self.env.user.login)
                integration_service = TaskIntegrationService(self.env)
                integration_service.update(vals, record, self.env.user)
        else:
            self.write({"changed_by_is": "no"})

        return record

    def to_dict(self):
        self.ensure_one()
        result = {}
        for field in self._fields:
            if field in [
                "__last_update",
                "create_date",
                "write_date",
                "external_id",
                "id",
                "changed_by_is",
            ]:
                continue
            f = self._fields[field]
            if (
                not isinstance(f, fields.Many2one)
                and not isinstance(f, fields.Many2many)
                and not isinstance(f, fields.One2many)
                and self[field]
            ):
                result[field] = self[field]
                if isinstance(self[field], datetime):
                    result[field] = self[field].isoformat()
        print(result)
        return result
