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

from openerp.osv import osv
from openerp.tools.translate import _

class pos_order(osv.osv):
    _inherit = "pos.order"

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')
        stock_location_obj = self.pool['stock.location']

        for order in self.browse(cr, uid, ids, context=context):
            if all(t == 'service' for t in order.lines.mapped('product_id.type')):
                continue
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery',False),
                    'date_done' : order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

            move_list = []
            for line in order.lines:
                if line.product_id and line.product_id.type == 'service':
                    continue
                if line.product_id.return_ok or line.product_id.container_ok:
                    location_stock_ids = stock_location_obj.search(cr, uid, [
                        ('company_id','=',order.company_id.id),
                        ('name','=','Stock'),
                        ], context=context)
                    location_tank_ids = stock_location_obj.search(cr, uid, [
                        ('company_id','=',order.company_id.id),
                        ('name','=','Tanks'),
                        ], context=context)
                    if line.product_id.return_ok:
                        location_id = location_tank_ids and location_tank_ids[0] or False
                        destination_id = location_stock_ids and location_stock_ids[0] or False
                    else:
                        location_id = location_stock_ids and location_stock_ids[0] or False
                        destination_id = location_tank_ids and location_tank_ids[0] or False

                move_list.append(move_obj.create(cr, uid, {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'picking_type_id': picking_type.id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.qty),
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else location_id,
                }, context=context))

            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
                picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                move_obj.force_assign(cr, uid, move_list, context=context)
                move_obj.action_done(cr, uid, move_list, context=context)
        return True

"""
class pos_order_line(osv.osv):
    _inherit = "pos.order.line"

    def onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False, context=None):
        context = context or {}
        res = super(pos_order_line, self).product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
                partner_id=partner_id, context=context)
        if product_id and res.get('value', False):
            prod = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if prod.return_ok:
                res['value'].update(qty = -(res['value'].get('qty', 1.0)) or -1.0)
        return res

    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        res = super(pos_order_line, self)._amount_line_all(cr, uid, ids, field_names, arg, context=context)
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            taxes_ids = [ tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id ]
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)

            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['price_subtotal'] = taxes['total']
            res[line.id]['price_subtotal_incl'] = taxes['total_included']
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line_all, multi='pos_order_line_amount', digits_compute=dp.get_precision('Product Price'), string='Subtotal w/o Tax', store=True),
        }
    """

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
