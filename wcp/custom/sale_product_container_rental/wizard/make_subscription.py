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

from openerp.osv import fields,osv
from openerp.tools.translate import _
from datetime import timedelta, datetime

class analytic_make_subscription(osv.osv_memory):
    _name = "analytic.make.subscription"
    _description = "Make Subscription for Service Calls from Analytic Account"

    def _get_qty(self, cr, uid, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id', False)
        res = False
        if active_id:
            res = self.pool.get('account.analytic.account').browse(cr, uid, active_id, context=context).quantity_max
        return res

    def _get_date(self, cr, uid, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id', False)
        aa_obj = self.pool.get('account.analytic.account')
        res = False
        if active_id:
            # Add 8 hours so it doesn't default to midnight
            date_start = datetime.strptime(aa_obj.browse(cr, uid, active_id, context=context).date_start, '%Y-%m-%d')
            res = ((date_start + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
        return res

    _columns = {
        'interval_number': fields.integer('Interval Qty'),
        'interval_type': fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
        'exec_init': fields.integer('Number of Service Calls'),
        'date_init': fields.datetime('First Date'),
        }

    _defaults = {
        'interval_number': 1,
        'interval_type': 'months',
        'exec_init': _get_qty,
        'date_init': _get_date,
        }

    def make_first_service_call(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return False

    def make_subscription(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not context.get('active_id', False):
            raise osv.except_osv(_('Error!'), ('Can\'t find the Analytic Account. Make sure to run the wizard from the Analytic Account form'))
        sub_data = self.read(cr, uid, ids, context=context)[0]
        sub_id = self.make_first_service_call(cr, uid, ids, context=context)

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
