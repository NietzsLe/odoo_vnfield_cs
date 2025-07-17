# -*- coding: utf-8 -*-
#############################################################################
#
#    VN Field Contractor System 
#    Enhanced Contractor Model với External Integration
#
#############################################################################

from odoo import models, fields, api

# ═══════════════════════════════════════════════════════════
# ═             👥 ENHANCED CONTRACTOR MODEL               ═
# ═══════════════════════════════════════════════════════════

class Contractor(models.Model):
    _inherit = "vnfield.contractor"
    _description = "Enhanced Contractor Model với IS Integration"

    # ─────────────── 🌐 EXTERNAL INTEGRATION FIELDS ───────────────
    external_id = fields.Integer(
        string="External ID",
        help="ID của contractor trên Integration System (IS)",
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
            'name': self.name
        }
    
    def _prepare_is_sync_data(self):
        """
        📊 Prepare data for Integration System synchronization
        """
        return {
            'name': self.name,
            'email': self.email if hasattr(self, 'email') else False,
            'phone': self.phone if hasattr(self, 'phone') else False,
            'active': self.active
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
- vnfield.contractor: Base contractor model được inherit
- name: Contractor name field
- email: Contact email field
- phone: Contact phone field  
- active: Boolean field cho record status

🔗 EXTERNAL INTEGRATION:
- external_id: Maps to Integration System contractor records
- JSON-RPC: Communication protocol với IS
- API responses: Dictionary format for external consumption

🔗 BUSINESS LOGIC DEPENDENCIES:
- Multi-site contractor management: CS ↔ IS contractor synchronization
- Contract negotiation: External contractor mapping cho agreement
- Task assignment: Cross-contractor task delegation
- Resource sharing: Contractor capacity và availability
"""
