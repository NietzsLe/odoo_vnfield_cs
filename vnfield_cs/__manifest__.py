# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════
# ═             🏗️ VNFIELD CONTRACTOR SYSTEM        ═
# ═   Multi-site contractor management với IS sync   ═
# ═══════════════════════════════════════════════════
#
#    Original Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Enhanced for contractor management by Assistant
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#############################################################################
{
    "name": "🏗️ VN Field Contractor System (CS)",
    "version": "17.0.2.0.0",
    "category": "Project Management", 
    "summary": "Multi-site contractor management với Integration System sync",
    "description": """
        🏗️ VN Field Contractor System (CS)
        ===================================
        
        ✨ Features:
        • 👷 Multi-site contractor management
        • 📄 Agreement management between contractors  
        • 📋 Enhanced task management và assignment
        • 🌐 JSON-RPC integration với Integration System (IS)
        • 🔄 Kafka message broker cho change propagation
        • 📊 Professional kanban và form views
        • 🎯 Workflow automation và approval processes
        
        🔧 Technical:
        • Odoo 17.0 compatible
        • REST API integration
        • External system synchronization
        • Modern UI/UX design
    """,
    "author": "VN Field Team",
    "website": "https://vnfield.com",
    "depends": [
        "base", 
        "mail", 
        "vnfield",
    ],
    "external_dependencies": {
        "python": ["confluent_kafka"],
    },
    "data": [
        "data/kafka_config.xml",
        "views/enhanced_views.xml",
    ],
    "demo": [],
    "images": ["static/description/banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
