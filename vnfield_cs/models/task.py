# -*- coding: utf-8 -*-
#############################################################################
#
#    VN Field Contractor System 
#    Enhanced Task Model với External Integration
#
#############################################################################

from odoo import models, fields, api

# ═══════════════════════════════════════════════════════════
# ═             📋 ENHANCED TASK MODEL                     ═
# ═══════════════════════════════════════════════════════════

class Task(models.Model):
    _inherit = "vnfield.task"
    _description = "Enhanced Task Model với IS Integration"

    # ─────────────── 🌐 EXTERNAL INTEGRATION FIELDS ───────────────
    external_id = fields.Integer(
        string="External ID",
        help="ID của task trên Integration System (IS)",
        copy=False,
        readonly=True
    )

    # ─────────────── 🔧 INTEGRATION HELPER METHODS ───────────────
    
    @api.model
    def get_external_reference(self):
        """
        📞 Get external system reference cho API calls
        """
        return {
            'external_id': self.external_id,
            'name': self.name,
            'code': self.code if hasattr(self, 'code') else False
        }
    
    def _prepare_is_sync_data(self):
        """
        📊 Prepare data for Integration System synchronization
        """
        return {
            'name': self.name,
            'description': self.description if hasattr(self, 'description') else False,
            'deadline': self.deadline.isoformat() if self.deadline else False,
            'status': self.status,
            'priority': self.priority if hasattr(self, 'priority') else False,
            'assignee_id': self.assignee_id.external_id if self.assignee_id and self.assignee_id.external_id else False,
            'project_id': self.project_id.external_id if self.project_id and hasattr(self.project_id, 'external_id') else False
        }
    


# ═══════════════════════════════════════════════════════════
# ═           🏗️ SYMBOL DEPENDENCIES ANALYSIS              ═
# ═══════════════════════════════════════════════════════════

"""
📋 DEPENDENCIES ĐƯỢC SỬ DỤNG TRONG FILE NÀY:

🔗 INTERNAL ODOO DEPENDENCIES:
- odoo.models.Model: Base class cho Odoo models
- odoo.fields: Field types (Integer)
- odoo.api: Decorators (@api.model)

🔗 VNFIELD BASE DEPENDENCIES:
- vnfield.task: Base task model được inherit
- name: Task name field
- description: Task description Text field
- deadline: Datetime field cho task deadline
- status: Selection field cho task status
- priority: Selection field cho task priority
- assignee_id: Many2one đến res.users
- project_id: Many2one đến vnfield.project

🔗 EXTERNAL INTEGRATION:
- external_id: Maps to Integration System task records
- JSON-RPC: Communication protocol với IS
- API responses: Dictionary format for external consumption

🔗 BUSINESS LOGIC DEPENDENCIES:
- Task lifecycle management: Status tracking và workflow
- Cross-contractor assignments: External user assignment
- Project coordination: Multi-site project task sync
- Progress tracking: Task completion và reporting
"""
