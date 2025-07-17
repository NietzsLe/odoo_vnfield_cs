# -*- coding: utf-8 -*-
#############################################################################
#
#    VN Field Contractor System 
#    Enhanced Approval Step Model với External Integration
#
#############################################################################

from odoo import models, fields, api

# ═══════════════════════════════════════════════════════════
# ═             ✅ ENHANCED APPROVAL STEP MODEL            ═
# ═══════════════════════════════════════════════════════════

class ApprovalStep(models.Model):
    _inherit = "vnfield.approval.step"
    _description = "Enhanced Approval Step Model với IS Integration"

    # ─────────────── 🌐 EXTERNAL INTEGRATION FIELDS ───────────────
    external_id = fields.Integer(
        string="External ID",
        help="ID của approval step trên Integration System (IS)",
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
            'step_sequence': self.sequence if hasattr(self, 'sequence') else 0
        }
    
    def _prepare_is_sync_data(self):
        """
        📊 Prepare data for Integration System synchronization
        """
        return {
            'name': self.name,
            'status': self.status,
            'approver_id': self.approver_id.external_id if self.approver_id and self.approver_id.external_id else False,
            'approval_id': self.approval_id.external_id if self.approval_id and hasattr(self.approval_id, 'external_id') and self.approval_id.external_id else False,
            'comment': self.comment if hasattr(self, 'comment') else False,
            'reviewed_at': self.reviewed_at.isoformat() if hasattr(self, 'reviewed_at') and self.reviewed_at else False
        }



# ═══════════════════════════════════════════════════════════
# ═           🏗️ SYMBOL DEPENDENCIES ANALYSIS              ═
# ═══════════════════════════════════════════════════════════

"""
📋 DEPENDENCIES ĐƯỢC SỬ DỤNG TRONG FILE NÀY:

🔗 INTERNAL ODOO DEPENDENCIES:
- odoo.models.Model: Base class cho Odoo models
- odoo.fields: Field types (Integer, Selection)
- odoo.api: Decorators (@api.model)

🔗 VNFIELD BASE DEPENDENCIES:
- vnfield.approval.step: Base approval step model được inherit
- name: Step name/description field
- status: Selection field (waiting, in-progress, approved, rejected)
- approver_id: Many2one to res.users
- approval_id: Many2one to vnfield.approval
- sequence: Integer field cho step ordering
- comment: Text field cho approval comments
- reviewed_at: Datetime field cho review timestamp

🔗 EXTERNAL INTEGRATION:
- external_id: Maps to Integration System approval step records
- JSON-RPC: Communication protocol với IS
- API responses: Dictionary format for external consumption

🔗 BUSINESS LOGIC DEPENDENCIES:
- Sequential approval workflow: Step ordering và processing
- User permissions: Approver assignment và validation
- Status tracking: Workflow state management
- Multi-site sync: CS ↔ IS approval step synchronization
- Review process: Comment và timestamp tracking
"""
