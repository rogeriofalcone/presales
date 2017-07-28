
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

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        vals = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        if line.product_id.return_ok or line.product_id.container_ok:
            domain = [('company_id','=',order.company_id.id)]
            if line.product_id.return_ok:
                domain.append(('name','=','Stock'))
            else:
                domain.append(('name','=','Tanks'))
            location_ids = self.pool['stock.location'].search(cr, uid, domain, context=context)
            vals.update(location_id = location_ids and location_ids[0] or False)
            vals.update(route_ids = line.route_id and [(4, line.route_id.id)] or [])
        else:
            location_id = order.partner_shipping_id.property_stock_customer.id
            vals['location_id'] = location_id
            vals['partner_dest_id'] = order.partner_shipping_id.id
        vals['warehouse_id'] = order.warehouse_id and order.warehouse_id.id or False
        return vals

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position,
                flag=flag, context=context)
        '''
        if product and res.get('value', False):
            prod = self.pool['product.product'].browse(cr, uid, product, context=context)
            if prod.return_ok:
                res['value'].update(price_unit = -(res['value'].get('price_unit', 0.0)) or 0.0)
        '''
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
