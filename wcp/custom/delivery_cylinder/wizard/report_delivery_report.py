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

from openerp.osv import osv, fields
from datetime import datetime, timedelta


class route_delivery_report(osv.osv_memory):
    _name = 'route.delivery.report'
    _description = 'Route Delivery Report'

    _columns = {
        'date': fields.date('Date'),
        'route_id': fields.many2one('delivery.route', 'Route'),
        'route_instance_id': fields.many2one('delivery.route.instance', 'Route',
            required=True, ondelete='cascade'),
        }

    _defaults = {
        'date': datetime.now() + timedelta(days= 7-datetime.now().weekday() if \
                datetime.now().weekday()>3 else 1),
        }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the route and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        context = context or {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['route_instance_id'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'delivery_cylinder.report_route_delivery', data=datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

