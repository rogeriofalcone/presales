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

from openerp import models, fields,api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class account_analytic_delivery(models.Model):
    _inherit = 'account.analytic.delivery'

    delivery_route_id = fields.Many2one('delivery.route','Route')
    route_interval_number = fields.Integer(related='delivery_route_id.interval_number',
        string="Route Interval",readonly=True)
    route_interval_type = fields.Selection(related='delivery_route_id.interval_type',
        string="Route Interval Type",readonly=True)
    skip_interval = fields.Integer('Skip / Countdown',default="1")

    @api.onchange("interval_number")
    def interval_number_change(self):
        if self.interval_number and self.delivery_route_id:
            self.skip_interval=self.interval_number
            next_call = datetime.strptime(self.delivery_route_id.date_next, DEFAULT_SERVER_DATE_FORMAT)
            self.nextcall = next_call + relativedelta(**{self.route_interval_type: self.interval_number})

    @api.onchange("delivery_route_id")
    def delivery_route_change(self):
        self.interval_number = self.delivery_route_id.interval_number

    @api.multi
    def write(self,vals):
        route_obj=self.env['delivery.route']
        if vals.get('delivery_route_id'):
            picking_obj = self.env['stock.picking']
            route_brw = route_obj.browse(vals.get('delivery_route_id'))
            if route_brw.date_next:
                next_call = datetime.strptime(route_brw.date_next, DEFAULT_SERVER_DATETIME_FORMAT)
                nextcall=next_call + relativedelta(**{route_brw.interval_type: route_brw.interval_number})
                vals.update({'nextcall':nextcall,'interval_number':route_brw.interval_number})
            if self.sale_id:
                date_to = (datetime.now() + relativedelta(months=+1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                picking_ids = picking_obj.search([
                    ('group_id', '=', self.sale_id.procurement_group_id.id),
                    ('state','not in',['done','cancel']),
                    ('min_date','<=',date_to),
                    ])
                picking_ids.write({'route_id': vals['delivery_route_id']})

        return super(account_analytic_delivery,self).write(vals)

    @api.multi
    def get_route_locations(self, route_id=False):
        """
        Gets all the unique locations either for a specific route or all route instances
        returns: list of location ids
        """
        domain = [('date_end','>=',fields.Date.context_today(self))]
        if route_id:
            domain.append(('delivery_route_id','=',route_id))
        deliverys = self.search(domain, order='sequence')
        location_ids = [x.location_id.id or x.account_id.partner_id.id for x in deliverys]
        return list(set(location_ids))

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    def action_view_delivery_lines(self):
        delivery_ids=self.delivery_ids
        return {
            'name': _('Contract Delivery Schedule'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.analytic.delivery',
            'context':{'show_address':1},
            'domain': str([('id', 'in', [pic.id for pic in delivery_ids])]),
        }

"""
class account_analytic_product_rental(models.Model):
    _inherit = "account.analytic.product.rental"

    interval_number = fields.Integer("Interval Number")
    interval_type = fields.Selection([
                        ('days','Days'),
                        ('weeks','Weeks'),
                        ('months','Months'),
            ], string='Interval Type', index=True, required=True,
            default='months', copy=False)
    nextcall = fields.Datetime("Next Delivery")
    partner_id = fields.Many2one("res.partner",'Location')

    @api.onchange("interval_number","interval_type")
    def onchange_int_num_type(self):
        self.nextcall = datetime.datetime.now()+ \
            relativedelta(**{self.interval_type: self.interval_number})
"""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
