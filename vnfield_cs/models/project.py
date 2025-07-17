# -*- coding: utf-8 -*-
#############################################################################
#
#    VN Field Contractor System 
#    Enhanced Project Model với External Integration
#
#############################################################################

from odoo import models, fields, api

# ═══════════════════════════════════════════════════════════
# ═             🚀 ENHANCED PROJECT MODEL                  ═
# ═══════════════════════════════════════════════════════════

class Project(models.Model):
    _inherit = "vnfield.project"
    _description = "Enhanced Project Model với IS Integration"

    # ─────────────── 🌐 EXTERNAL INTEGRATION FIELDS ───────────────
    external_id = fields.Integer(
        string="External ID",
        help="ID của project trên Integration System (IS)",
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
            'project_code': self.code
        }
    
    def _prepare_is_sync_data(self):
        """
        📊 Prepare data for Integration System synchronization
        """
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else False,
            'end_date': self.end_date.isoformat() if self.end_date else False,
            'budget': self.budget,
            'actual_cost': self.actual_cost,
            'progress': self.progress,
            'manager_id': self.manager_id.external_id if self.manager_id and self.manager_id.external_id else False,
            'project_owner_id': self.project_owner_id.external_id if self.project_owner_id and self.project_owner_id.external_id else False
        }



# ═══════════════════════════════════════════════════════════
# ═           🏗️ SYMBOL DEPENDENCIES ANALYSIS              ═
# ═══════════════════════════════════════════════════════════

"""
📋 DEPENDENCIES ĐƯỢC SỬ DỤNG TRONG FILE NÀY:

🔗 INTERNAL ODOO DEPENDENCIES:
- odoo.models.Model: Base class cho Odoo models
- odoo.fields: Field types (Integer, Boolean)
- odoo.api: Decorators (@api.model)

🔗 VNFIELD BASE DEPENDENCIES:
- vnfield.project: Base project model được inherit
- code: Auto-generated project code field  
- name, description: Basic project information fields
- status: Selection field (draft, planning, in-progress, etc.)
- priority: Selection field (high, medium, low)
- start_date, end_date: Date range fields
- budget, actual_cost: Monetary fields
- progress: Float field (percentage)
- manager_id: Many2one to res.users
- project_owner_id: Many2one to vnfield.contractor
- task_ids: One2many to vnfield.task
- member_ids: Many2many to res.users

🔗 EXTERNAL INTEGRATION:
- external_id: Maps to Integration System project records
- JSON-RPC: Communication protocol với IS
- API responses: Dictionary format for external consumption

🔗 BUSINESS LOGIC DEPENDENCIES:
- Project workflow: Status transitions và lifecycle management
- Team management: Manager, owner, members
- Financial tracking: Budget vs actual cost
- Progress monitoring: Task completion percentage
- Multi-site sync: CS ↔ IS project synchronization
"""
