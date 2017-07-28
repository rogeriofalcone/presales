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
        'name': 'Load MID:COM Deliveries',
        'version': '0.1',
        'category': 'Propane',
        'description': """
            Load MID:COM Deliveries
        """,
        'author': 'Simplify Solutions',
        'website': 'www.simplifycloud.com',
        'depends': ['delivery_cylinder'],
        'data': [
            'wizard/load_midcom_view.xml',
            'views/delivery_midcom.xml',
        ],
        'qweb' : [
                  "static/src/xml/midcom.xml",
                  ],
        'installable': True,
        'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
