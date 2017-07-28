# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution...
#    Copyright (C) 2004-2015 Simplify Solutions. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : 'Rental Contracts - Will Calls',
    'version': '0.1',
    'author': 'Simplfy Solutions',
    'maintainer': 'Simplfy Solutions',
    'website': 'http://www.simplifycloud.com.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Rental Contract Will Calls',
    'description': """
Rental Contract Will Calls
=================================

        1. 
        2. 

Contributors
------------
* John Boyle (john.boyle@simplifycloud.com)
""",
    "category" : "Generic Modules/CRM",
    "depends" : ["crm","stock","sale_product_container_rental",'delivery_route'],
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
        "wizard/make_willcall_view.xml",
        "views/analytic_view.xml",
        "views/crm_view.xml",
        ],
    'update_xml': [
        ],
    "installable": True,
    "active": False,
    'certificate': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
