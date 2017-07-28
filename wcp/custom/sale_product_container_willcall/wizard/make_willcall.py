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

from datetime import datetime, timedelta
from openerp import models,api,fields,_
from openerp.exceptions import except_orm

class analytic_willcall(models.TransientModel):
    _name = 'analytic.willcall'
    _description = 'Make Will Call'

    def _get_locations(self):
        res = []
        list_loc = []
        acc_obj = self.env['account.analytic.account']
        delivery_obj = self.env['account.analytic.delivery']
        context = self._context
        if context.get('active_model') == 'account.analytic.delivery' and context.get('active_ids'):
            accounts = [x.account_id for x in delivery_obj.browse(self._context.get('active_ids'))]
        elif context.get('active_model') == 'crm.phonecall' and context.get('active_id'):
            phonecall_obj = self.env['crm.phonecall']
            phonecall = phonecall_obj.browse(context['active_id'])
            if not phonecall.partner_id:
                raise except_orm(_('Warning!'),
                        _("A partner must be specified to create a Will Call"))
            accounts = acc_obj.search([('partner_id','=',phonecall.partner_id.id)])
        else:
            accounts = [x for x in acc_obj.browse(self._context.get('active_ids'))]
        for act in accounts:
            loc_ids = [x.location_id.id for x in act.delivery_ids]
            if loc_ids:
                for loc in loc_ids:
                    list_loc.append(loc)
            res = [('id','in',[x for x in list_loc])]
        return res

    def _get_default_location(self):
        res = self._get_locations()
        return res and res[0][2] and res[0][2][0] or []

    def _get_routes(self):
        route_obj = self.env['delivery.route.instance']
        if self.date:
            domain = [('date','=',self.date)]
        else:
            domain = [('date','>=',fields.Date.context_today(self))]
        route_ids=route_obj.search(domain)
        if route_ids:
            return [x.id for x in route_ids]
        return []

    line_ids = fields.One2many('analytic.willcall.line','willcall_id','Lines')
    location_id = fields.Many2one('res.partner', 'Location',
                        domain=lambda self: self._get_locations(),
                        default=lambda self: self._get_default_location())
    route_id = fields.Many2one('delivery.route.instance','Route Instance')
    date = fields.Date('Date', default=datetime.now() + \
            timedelta(days= 7-datetime.now().weekday() if datetime.now().weekday()>3 else 1))
    # route_id = fields.Many2one('delivery.route.instance','Route Instance')

    @api.model
    def default_get(self, fields):
        res = super(analytic_willcall, self).default_get(fields)
        context = self._context
        if context.get('active_model') == 'account.analytic.delivery' and context.get('active_ids'):
            res['line_ids'] = []
            delivery_obj = self.env['account.analytic.delivery']
            for line in delivery_obj.browse(context['active_ids']):
                res['line_ids'].append((0,0, {
                    'product_id': line.product_id.id,
                    'merge_qty': line.quantity,
                    }))
        return res

    @api.onchange('location_id')
    def onchange_location_id(self):
        acc_obj = self.env['account.analytic.account']
        delivery_obj = self.env['account.analytic.delivery']
        context = self._context
        if self.location_id:
            pro_list = []
            qtylist = []
            new_dict = []
            #TODO: set the damn account on the wizard
            if context.get('active_model') == 'account.analytic.delivery' and context.get('active_ids'):
                accounts = [x.account_id for x in delivery_obj.browse(self._context.get('active_ids'))]
            elif context.get('active_model') == 'crm.phonecall' and context.get('active_id'):
                phonecall_obj = self.env['crm.phonecall']
                phonecall = phonecall_obj.browse(context['active_id'])
                if not phonecall.partner_id:
                    raise except_orm(_('Warning!'),
                            _("A partner must be specified to create a Will Call"))
                accounts = acc_obj.search([('partner_id','=',phonecall.partner_id.id)])
            else:
                accounts = [x for x in acc_obj.browse(self._context.get('active_ids'))]
            for act in accounts:
                prod_list = list(set([x.product_id for x in act.delivery_ids]))
            for act in accounts:
                for prod in prod_list:
                    new_qty=0.0
                    for x in act.delivery_ids:
                        if x.location_id == self.location_id and x.product_id==prod:
                            pro_list.append(x.product_id.id)
                            qtylist.append(x.quantity)
                            delivery_line=x.id
                            new_qty+=x.quantity
                    if new_qty>0:
                        dict={
                            'qty':new_qty,
                            'product':prod,
                            'delivery_line':delivery_line
                        }
                        new_dict.append(dict)
                self.line_ids = [(0,0, {'product_id': x['product'],
                    'merge_qty': x['qty'],'quantity': 0.0,
                    'delivery_line':x['delivery_line']
                    }) for x in new_dict]

    @api.multi
    def create_willcall(self):
        cylinder_obj = self.env['delivery.propane']
        delivery_ids = []
        if self.line_ids:
            for line in self.line_ids:
                '''
                if line.quantity>line.merge_qty:
                    raise orm.except_orm(
                            _('Error:'),
                            _("%s qty should not be exceed ")
                            % (line.product_id.name))
                '''
                if line.quantity > 0.0:
                    cylinder_vals = {
                        'product_id':line.product_id.id,
                        'location_id': self.location_id.id,
                        'schedule_in':line.quantity,
                        'schedule_out':line.quantity,
                        'actual_in':line.quantity,
                        'actual_out':line.quantity,
                        'delivery_date': self.route_id.date,
                        'partner_id':line.delivery_line.location_id.id,
                        'project_id':line.delivery_line.account_id.id,
                        'delivery_route_id':self.route_id.id,
                        'price_unit':line.delivery_line.sale_line_id.price_unit,
                        'type': 'cylinder',
                    }
                    if self._context.get('active_model') == 'crm.phonecall' \
                            and self._context.get('active_id', False):
                        cylinder_vals.update(
                                phonecall_id = self._context['active_id'],
                                )
                        phonecall_obj = self.env['crm.phonecall']
                        phonecall = phonecall_obj.browse(self._context['active_id'])
                        phonecall.write({'willcall': True})
                    delivery_ids.append(cylinder_obj.create(cylinder_vals))
        return True
        return {
            'name': 'Propane Deliveries',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'delivery.propane',
            'domain': "[('id','in', [x.id for x in delivery_ids])]",
            }

class analytic_willcall_line(models.TransientModel):
    _name = 'analytic.willcall.line'
    _description = 'Will Call Line'

    product_id = fields.Many2one('product.product', 'Product')
    quantity = fields.Float('Quantity')
    willcall_id = fields.Many2one('analytic.willcall','Will Call')
    merge_qty = fields.Float('Estimated Quantity')
    delivery_line = fields.Many2one('account.analytic.delivery','Delivery Line')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
