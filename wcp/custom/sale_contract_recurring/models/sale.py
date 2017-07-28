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

from openerp import models, api, fields
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
import datetime
from dateutil.relativedelta import relativedelta

class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def get_lines(self, order_line, date_order):
        order_line_list = []
        rental_obj = self.env['account.analytic.product.rental']
        for line in order_line:
            if line.product_id.container_ok and line.product_id.bom_ids:
                prod_obj = self.pool['product.product']
                bom_obj = self.pool['mrp.bom']
                bom_exploded = bom_obj._bom_explode(self._cr, self._uid, line.product_id.bom_ids[0],
                        line.product_id.id, line.product_uom_qty,
                        properties=None, routing_id=None, context=self._context)
                for bom_line in bom_exploded[0]:
                    bl_product = prod_obj.read(self._cr, self._uid, bom_line.get('product_id'),
                            ['container_ok', 'rental_ok', 'rental_price'
                                'uom_id'], context=self._context)
                    if bl_product.get('rental_ok'):
                        product = prod_obj.browse(self._cr, self._uid, bom_line['product_id'],
                                context=self._context)
                        break
            elif line.product_id.rental_ok or line.rent_type == 'rent':
                product = line.product_id
                #FIXME: use real strptime()
                if line.start_date < date_order.split(' ')[0]:
                    raise orm.except_orm(
                        _('Error:'),
                        _("%s start date should not be less than Order Date")%
                        (line.name))
                if line.product_uom_qty <= 0.0:
                    raise orm.except_orm(
                        _('Error:'),
                        _("Quantity Should not be less than 0.0"))
                #FIXME: combine the date checks
                if line.start_date and line.end_date:
                    date_after_month = (datetime.datetime.strptime(
                        line.start_date,DEFAULT_SERVER_DATE_FORMAT) + \
                        relativedelta(months = 1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                    if date_after_month > line.end_date:
                        raise orm.except_orm(
                            _('Error:'),_("%s product end date at least 1 \
                                month exceed from start date") % (line.name))
            else:
                continue
            if product.track_outgoing or product.track_all:
                count = int(line.product_uom_qty)
            else:
                if [x.get('product_id') for x in order_line_list if \
                        x == product.id] or rental_obj.search([
                    ('analytic_account_id','=',self.project_id.id),
                    ('analytic_account_id.type','=','contract'),
                    ('product_id','=',product.id),
                    ]):
                        continue
                count = 1
            for i in range(count):
                line_vals = {
                    'product_id': product.id,
                    'name': product.description or product.name or line.name,
                    'date_start': line.start_date,
                    'date_end': line.end_date,
                    'price_unit': line.rental_price_unit or line.price_unit,
                    'uom_id': line.product_uom.id,
                    'sale_line_id': line.id,
                    'nextcall': line.start_date,
                    'interval_number': 1,
                    'interval_type': product.default_interval_type or 'months',
                    'partner_id': line.order_id.partner_invoice_id.id,
                    }
                order_line_list.append((0, 0, line_vals))

        return order_line_list

    @api.multi
    def delivery_lines(self,order_line,date_order):
        order_line_list = []
        for line in order_line:
            if line.product_id.container_ok is True:
                if line.product_id.container_ok is True:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'name':line.name,
                        'location_id':line.order_id.partner_shipping_id.id or line.partner_id.id,
                        'quantity':line.product_uom_qty,
                        'sale_line_id':line.id,
                        'interval_type':'months',
                        'interval_number':1,
                        'nextcall': datetime.date.today() + relativedelta(months=1),
                        'numbercall':-1,
                        }
                    order_line_list.append((0, 0, line_vals))
        return order_line_list

    @api.multi
    def action_wait(self):
        res = super(sale_order, self).action_wait()
        line_data = []
        analytic_obj = self.env['account.analytic.account']
        loc_obj = self.env['stock.location']
        for order in self:
            loc_id = order.partner_id.property_stock_customer_rental
            delivery_data = self.delivery_lines(order.order_line,order.date_order)
            line_data = self.get_lines(order.order_line,order.date_order)
            if not line_data and not delivery_data:
                continue
            pre_contract = analytic_obj.search(
                [('partner_id','=',order.partner_id.id),('type','=','contract')])
            if not pre_contract:
                parent_id = analytic_obj.search([('code','=','CONT')])
                pre_contract = analytic_obj.create({
                    'name': order.partner_id.name,
                    'type': 'contract',
                    'use_delivery': True,
                    'partner_id': order.partner_id.id,
                    'amount_max': order.amount_total,
                    'parent_id': parent_id and parent_id[0] or False,
                    })
                order.write({'project_id': pre_contract.id})
            if not loc_id:
                parent_location_id = loc_obj.search([('name','=','Rental Out')],limit=1)
                loc_id = loc_obj.create({
                    'name': order.partner_id.name,
                    'usage': 'internal',
                    'location_id': parent_location_id.id or False,
                    })
            pre_contract.write({
                'rental_product_line_ids': (line_data if line_data else []),
                'delivery_ids': (delivery_data if delivery_data else []),
                'amount_max': (pre_contract.amount_max + order.amount_total),
                })
            order.write({'project_id': pre_contract.id})
            if not order.partner_id.property_stock_customer_rental:
                order.partner_id.write({
                    'property_stock_customer_rental': loc_id.id
                    })
        return res
 
    @api.model
    def _prepare_order_line_procurement(
            self, order, line, group_id=False):
        res = super(sale_order, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        rule_obj = self.env['procurement.rule']
        loc_obj = self.env['stock.location']
        stok_loc_obj = self.env['stock.location.path']
        route_obj = self.env['stock.location.route']
        rent_in_id = loc_obj.search([('name','=','Rental In')], limit = 1)
        rent_out_id = self.partner_id.property_stock_customer_rental
        if not rent_out_id:
            rent_out_id = loc_obj.search([('name','=','Rental Out')], limit = 1)
        route_id=route_obj.search([('name','=','Rental Product')],limit=1)
        # Set schedule date for delivery order as line start date
        if line.start_date:
            res.update({'date_planned':line.start_date})
        if (line.product_id and line.product_id.rental_ok is True and \
            line.rent_type=='rent'):
            rule_exist=rule_obj.search([('name','=',order.partner_id.name)])
            if not rule_exist:
                rule_id_del = rule_obj.create({
                    'name': order.partner_id.name,
                    'location_id': order.partner_id.property_stock_customer_rental.id,
                    'location_src_id': rent_in_id.id,
                    'action': 'move',
                    'route_id': route_id.id,
                    'picking_type_id': order.warehouse_id.out_type_id.id,
                    'warehouse_id': order.warehouse_id.id}
                    )
                stok_loc_obj.create({
                    'name':order.partner_id.name,
                    'location_from_id': order.partner_id.property_stock_customer_rental.id,
                    'location_dest_id': rent_in_id.id,
                    'route_id': route_id.id,
                    'auto': 'auto',
                    'invoice_state': 'none',
                    'picking_type_id': order.warehouse_id.in_type_id.id,
                    'warehouse_id': order.warehouse_id.id,
                })
                res.update({
                    'location_id': order.partner_id.property_stock_customer_rental.id,
                    'rule_id':rule_id_del.id,
                    })
            else:
                res.update({
                    'location_id': order.partner_id.property_stock_customer_rental.id,
                    'rule_id':rule_exist.id,
                    })
        if (line.product_id and line.product_id.container_ok is True):
            rule_cylin = rule_obj.search([('name','=','Cylinder')])
            res.update({
                    'location_id': rent_out_id.id,
                    'rule_id': rule_cylin.id,
                    })
        print"thissss is res",res
        return res

class sale_order_line(models.Model):
    _inherit ='sale.order.line'

    rental_price_unit = fields.Float(string='Rental Price',digits=dp.get_precision('Account'))
    rent_type = fields.Selection([('rent','Rent'),('sell','Sell'),
            ('rent_sell','Rent-Sell')],'Rental Type',default='sell')
    prod_hidden = fields.Boolean('Tank/Cylinder')

    @api.onchange('start_date')
    def start_date_change(self):
        if self.start_date:
            if self.end_date and self.start_date > self.end_date:
                self.end_date = self.start_date
            date_after_month = datetime.datetime.strptime(
                self.start_date,DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=10)
            if self.end_date:
                number_of_days = (
                    fields.Date.from_string(self.end_date) -
                    fields.Date.from_string(self.start_date)).days + 1
                if self.number_of_days != number_of_days:
                    self.number_of_days = number_of_days
            self.end_date = date_after_month

    @api.v7
    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        product_obj = self.pool['product.product']
        product_uom_obj = self.pool['product.uom']
        product = product_obj.browse(cr, uid, product_id, context=context)
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if product.container_ok and not product.rental_ok:
            if product.bom_ids:
                price_unit, rental_price_unit = 0.0, 0.0
                bom_obj = self.pool['mrp.bom']
                bom_exploded = bom_obj._bom_explode(cr, uid, product.bom_ids[0],
                        product_id, qty, properties=None, routing_id=None, context=context)
                for bom_line in bom_exploded[0]:
                    bl_product = product_obj.read(cr, uid, bom_line.get('product_id'),
                            ['container_ok', 'rental_ok', 'rental_price', 'list_price',
                                'uom_id'], context=context)
                    if bl_product.get('rental_ok'):
                        rental_price_unit += bl_product.get('rental_price')
                    else:
                        price_unit += bl_product.get('list_price')
                        qty = product_uom_obj._compute_qty(cr, uid, bom_line['product_uom'],
                                bom_line['product_qty'], bl_product['uom_id'][0])
                        price_unit = self.pool['product.pricelist'].price_get(cr, uid,
                                [pricelist], bom_line['product_id'],
                                bom_line['product_qty'] or 1.0, partner_id, context)[pricelist]
                        price = price_unit * qty
                res['value'].update({
                    'rental_price_unit': rental_price_unit,
                    'price_unit': price,
                    'rent_type': 'rent',
                    })

        elif product.rental_ok:
            res['value'].update({
                'rental_price_unit': product.rental_price,
                'price_unit': 0.0,
                'prod_hidden': product.rental_ok,
                'rent_type': 'rent',
                })

        return res
