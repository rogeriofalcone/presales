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
    'name': 'Delivery Cylinder',
    'version': '1.1',
    'category': 'Delivery Cylinder',
    'description': """
        Delivery Cylinder
    """,
    'author': 'Bista Solutions Pvt Ltd',
    'website': 'www.bistasolutions.com',
    'depends': [
        'base',
        'sale_contract_recurring',
        'delivery_route',
        'analytic'
    ],
    'data': [
        'views/report_rental_contract.xml',
        'views/delivery_propane_view.xml',
        'wizard/merge_picking_view.xml',
        'views/report_delivery_route.xml',
        'delivery_propane_report.xml',
        'wizard/report_delivery_report.xml',
        'views/scheduler.xml',
        'views/res_company_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
