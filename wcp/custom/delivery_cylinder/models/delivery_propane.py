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

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from openerp.osv import orm

class stock_move(models.Model):
    _inherit = 'stock.move'

    def _action_explode_in(self, cr, uid, move, context=None):
        """ Explodes pickings.
        @param move: Stock moves
        @return: True
        """
        if context is None:
            context = {}
        bom_obj = self.pool.get('mrp.bom')
        move_obj = self.pool.get('stock.move')
        prod_obj = self.pool.get("product.product")
        proc_obj = self.pool.get("procurement.order")
        uom_obj = self.pool.get("product.uom")
        to_explode_again_ids = []
        property_ids = context.get('property_ids') or []
        bis = bom_obj._bom_find(cr, SUPERUSER_ID, product_id=move.product_id.id, properties=property_ids)
        bom_point = bom_obj.browse(cr, SUPERUSER_ID, bis, context=context)
        if bis and bom_point.type == 'phantom':
            processed_ids = []
            factor = uom_obj._compute_qty(cr, SUPERUSER_ID, move.product_uom.id, move.product_uom_qty, bom_point.product_uom.id) / bom_point.product_qty
            res = bom_obj._bom_explode(cr, SUPERUSER_ID, bom_point, move.product_id, factor, property_ids, context=context)

            for line in res[0]:
                product = prod_obj.browse(cr, uid, line['product_id'], context=context)
                if product.type != 'service' and product.rental_ok == True:
                    valdef = {
                        'picking_id': move.picking_id.id if move.picking_id else False,
                        'product_id': line['product_id'],
                        'product_uom': line['product_uom'],
                        'product_uom_qty': line['product_qty'],
                        'product_uos': line['product_uos'],
                        'product_uos_qty': line['product_uos_qty'],
                        'state': 'draft',  #will be confirmed below
                        'name': line['name'],
                        'procurement_id': move.procurement_id.id,
                        'split_from': move.id, #Needed in order to keep sale connection, but will be removed by unlink
                    }
                    mid = move_obj.copy(cr, uid, move.id, default=valdef, context=context)
                    to_explode_again_ids.append(mid)
                else:
                    if prod_obj.need_procurement(cr, uid, [product.id], context=context):
                        valdef = {
                            'name': move.rule_id and move.rule_id.name or "/",
                            'origin': move.origin,
                            'company_id': move.company_id and move.company_id.id or False,
                            'date_planned': move.date,
                            'product_id': line['product_id'],
                            'product_qty': line['product_qty'],
                            'product_uom': line['product_uom'],
                            'product_uos_qty': line['product_uos_qty'],
                            'product_uos': line['product_uos'],
                            'group_id': move.group_id.id,
                            'priority': move.priority,
                            'partner_dest_id': move.partner_id.id,
                            }
                        if move.procurement_id:
                            proc = proc_obj.copy(cr, uid, move.procurement_id.id, default=valdef, context=context)
                        else:
                            proc = proc_obj.create(cr, uid, valdef, context=context)
                        proc_obj.run(cr, uid, [proc], context=context) #could be omitted

            #check if new moves needs to be exploded
            if to_explode_again_ids:
                for new_move in self.browse(cr, uid, to_explode_again_ids, context=context):
                    processed_ids.extend(self._action_explode_in(cr, uid, new_move, context=context))

            if not move.split_from and move.procurement_id:
                # Check if procurements have been made to wait for
                moves = move.procurement_id.move_ids
                if len(moves) == 1:
                    proc_obj.write(cr, uid, [move.procurement_id.id], {'state': 'done'}, context=context)

            if processed_ids and move.state == 'assigned':
                # Set the state of resulting moves according to 'assigned' as the original move is assigned
                move_obj.write(cr, uid, list(set(processed_ids) - set([move.id])), {'state': 'assigned'}, context=context)

            #delete the move with original product which is not relevant anymore
            move_obj.unlink(cr, SUPERUSER_ID, [move.id], context=context)
            #return list of newly created move
            return processed_ids

        return [move.id]

class delivery_propane(models.Model):
    _name = 'delivery.propane'
    _description = 'Delivery Propane'
    _rec_name = 'product_id'

    location_id = fields.Many2one('res.partner','Location')
    product_id = fields.Many2one('product.product','Product')
    schedule_in = fields.Integer('Schedule In')
    schedule_out = fields.Integer('Schedule Out')
    actual_in = fields.Integer('Actual In')
    actual_out = fields.Integer('Actual Out')
    delivery_date = fields.Date('Date')
    project_id = fields.Many2one('account.analytic.account',string='Project')
    picking_in_id = fields.Many2one('stock.picking' ,string='Picking In')
    picking_out_id = fields.Many2one('stock.picking' ,string='Picking Out')
    delivery_route_id = fields.Many2one('delivery.route.instance','Delivery Route')
    price_unit = fields.Float('Price')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    sequence = fields.Integer('Sequence')
    type = fields.Selection([
            ('cylinder', 'Cylinder'),
            ('bulk', 'Bulk'),
            ], string="Type", default='bulk')

    state = fields.Selection([
            ('draft','New'),
            ('open','Delivered'),
            ('done','Done'),
            ('cancel','Cancelled'),
        ], string='Status', readonly=True, default='draft')

    _order = 'location_id, sequence'

    @api.multi
    def get_instance_locations(self, route_instance_id=False):
        """
        Gets all the unique locations either for a specific route instance or all route instances
        returns: list of location ids
        """
        domain = [('state','not in',['done','cancel'])]
        if route_instance_id:
            domain.append(('delivery_route_id','=',route_instance_id))
        deliverys = self.search(domain, order='sequence')
        location_ids = [x.location_id or x.project_id and x.project_id.partner_id for x in deliverys]
        return list(set(location_ids))

    @api.multi
    def create_pickings(self):
        loc_obj = self.env['stock.location']
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        rent_in_id = loc_obj.search([('name','=','Rental In')],limit=1)
        rent_out_id = self.location_id.property_stock_customer_rental or \
            loc_obj.search([('name','=','Rental Out')],limit=1)
        picking_vals, picking_in_vals = {}, {}
        move_out_list,move_in_list = [],[]
        for line in self:
            warehouse = line.delivery_route_id.route_id.fleet_id and line.delivery_route_id.route_id.fleet_id.warehouse_id
            move_out_vals = {
                'name': line.product_id.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uos': line.product_id.uom_id.id,
                'product_uom_qty': line.actual_out,
                'date': line.delivery_date,
                'date_expected': line.delivery_date,
                'location_id': rent_in_id.id,
                'location_dest_id': rent_out_id.id,
                'price_unit': line.price_unit,
                'partner_id': line.location_id.id
                }
            move_in_vals = {
                'name': line.product_id.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uos': line.product_id.uom_id.id,
                'product_uom_qty': line.actual_in,
                'date': line.delivery_date,
                'date_expected': line.delivery_date,
                'location_id': rent_out_id.id,
                'location_dest_id': rent_in_id.id,
                'price_unit': line.price_unit,
                'partner_id': line.location_id.id
                }
        move_out_list.append((0,0,move_out_vals))
        move_in_list.append((0,0,move_in_vals))
        if not warehouse:
            warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.company_id.id)])
        if move_out_list:
            picking_vals = {
                'picking_type_id': warehouse.out_type_id.id,
                'partner_id': line.location_id.id,
                'date': line.delivery_route_id.route_id.date_next,
                'origin': line.delivery_route_id.route_id.name,
                'move_lines':(move_out_list if move_out_list else []),
                'project_id': line.project_id.id,
                'delivery_route_id': line.delivery_route_id.id,
            }
            picking_out_id = picking_obj.create(picking_vals)
            self.write({'picking_out_id': picking_out_id.id})
            [move_obj._action_explode(ln) for ln in picking_out_id.move_lines]
            picking_out_id.move_lines.action_confirm()
            picking_out_id.force_assign()
            picking_out_id.action_done()
        if move_in_list:
            picking_in_vals = {
                'picking_type_id': warehouse.in_type_id.id,
                'partner_id': line.location_id.id,
                'date': line.delivery_route_id.route_id.date_next,
                'origin': line.delivery_route_id.route_id.name,
                'move_lines':(move_in_list if move_in_list else []),
                'project_id': line.project_id.id,
                'delivery_route_id': line.delivery_route_id.id,
            }
            picking_in_id = picking_obj.create(picking_in_vals)
            self.write({'picking_in_id': picking_in_id.id})
            [move_obj._action_explode_in(ln) for ln in picking_in_id.move_lines]
            picking_in_id.move_lines.action_confirm()
            picking_in_id.force_assign()
            picking_in_id.action_done()
        self.write({'state':'done'})
        return True

    @api.onchange("actual_in")
    def onchange_actual_in(self):
        if self.actual_in:
            if (self.actual_in-self.schedule_in)>=5 or \
            self.actual_in>=(self.schedule_in*2) \
             or self.actual_in<=0:
                raise orm.except_orm(
                            _('Error:'),
                            _("Actual In Qty is exceed than Schedule In Qty"))

    @api.onchange("actual_out")
    def onchange_actual_out(self):
        if self.actual_out:
            if (self.actual_out-self.schedule_out)>=5 or \
                self.actual_out>=(self.schedule_out*2) \
                 or self.actual_out<=0:
                raise orm.except_orm(
                            _('Error:'),
                            _("Actual Out Qty is exceed than Schedule Out Qty"))

class delivery_route_instance(models.Model):
    _inherit = 'delivery.route.instance'

    propane_ids = fields.One2many('delivery.propane', 'delivery_route_id', 'Delivery Propane')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
