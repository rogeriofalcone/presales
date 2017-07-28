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

from openerp import models, api

class merge_picking(models.TransientModel):
    _name = 'merge.picking'
    _description = 'Complete Deliveries'

    @api.multi
    def _make_invoices(self, deliveries, ln):
        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']
        invoices = []
        invoice_vals = {}
        invoice_line_list = []
        for delivery in deliveries:
            for line in ln:
                partner = delivery.location_id or \
                        delivery.project_id and delivery.project_id.partner_id
                val = line_obj.product_id_change(delivery.product_id.id,
                        False,partner_id=partner.id, fposition_id=False)
                res = val['value']
                #FIXME: Don't carry the price in the delivery line
                invoice_line_vals = {
                    'name': delivery.product_id.description_sale or line.name,
                    'product_id': delivery.product_id.id,
                    'uos_id': line.uom_id.id,
                    'account_id': delivery.product_id.categ_id.property_account_income_categ.id or \
                            delivery.product_id.property_account_income.id,
                    'account_analytic_id': delivery.project_id.id,
                    'quantity': delivery.actual_out,
                    'price_unit': delivery.price_unit or delivery.product_id.list_price,
                    'partner_id': partner.id,
                    'invoice_line_tax_id':[(6, 0, res.get('invoice_line_tax_id'))]
                    }
                invoice_line_list.append((0,0,invoice_line_vals))
            for picking in (delivery.picking_in_id, delivery.picking_out_id):
                picking.write({'invoice_state': 'invoiced'})
            if invoice_line_list:
                invoice_vals = {
                    'partner_id': partner.id,
                    'date_invoice': delivery.delivery_route_id.route_id.date_next,
                    'account_id': delivery.project_id.partner_id.property_account_receivable.id,
                    'invoice_line': invoice_line_list,
                }
                invoice = invoice_obj.create(invoice_vals)
                delivery.write({'invoice_id': invoice.id})
                invoices.append(invoice.id)
        invoice_obj.button_compute(invoices)
        return invoices

    @api.multi
    def _make_picking(self, deliveries, ln):
        loc_obj=self.env['stock.location']
        picking_obj=self.env['stock.picking']
        move_obj=self.env['stock.move']
        rent_in_id=loc_obj.search([('name','=','Rental In')],limit=1)
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.company_id.id)])
        picking_vals, picking_in_vals = {}, {}
        move_out_list,move_in_list = [],[]
        for delivery in deliveries:
            if delivery.picking_out_id:
                continue
            partner = delivery.location_id or \
                        delivery.project_id and delivery.project_id.partner_id

            for line in ln:
                move_out_vals = {
                            'name': line.name or '',
                            'product_id': line.id,
                            'product_uom': line.uom_id.id,
                            'product_uos': line.uom_id.id,
                            'product_uom_qty':delivery.actual_out,
                            'date': delivery.delivery_date,
                            'date_expected':delivery.delivery_date,
                            'location_id': rent_in_id.id,
                            'location_dest_id': partner.property_stock_customer_rental.id \
                                    or partner.parent_id.property_stock_customer_rental.id,
                            'price_unit': delivery.price_unit,
                            'partner_id': partner.id
                        }
                move_in_vals = {
                            'name': line.name or '',
                            'product_id': line.id,
                            'product_uom': line.uom_id.id,
                            'product_uos': line.uom_id.id,
                            'product_uom_qty': delivery.actual_in,
                            'date':  delivery.delivery_date,
                            'date_expected': delivery.delivery_date,
                            'location_id': partner.property_stock_customer_rental.id \
                                    or partner.parent_id.property_stock_customer_rental.id,
                            'location_dest_id':rent_in_id.id,
                            'price_unit': delivery.price_unit,
                            'partner_id': partner.id
                    }
            move_out_list.append((0,0,move_out_vals))
            move_in_list.append((0,0,move_in_vals))
            if move_out_list:
                picking_vals = {
                    'picking_type_id': warehouse.out_type_id.id,
                    'partner_id': partner.id,
                    'date': delivery.delivery_route_id.route_id.date_next,
                    'origin': delivery.delivery_route_id.route_id.fleet_id.name + '-' + delivery.delivery_route_id.route_id.name,
                    'move_lines':(move_out_list if move_out_list else []),
                    'project_id': delivery.project_id.id,
                    'delivery_route_id': delivery.delivery_route_id.id,
                    'invoice_state': '2binvoiced',
                }
                picking_out_id = picking_obj.create(picking_vals)
                delivery.write({'picking_out_id': picking_out_id.id})
                [move_obj._action_explode(x) for x in picking_out_id.move_lines]
                picking_out_id.move_lines.action_confirm()
                picking_out_id.force_assign()
                picking_out_id.action_done()
            if move_in_list:
                picking_in_vals = {
                    'picking_type_id': warehouse.in_type_id.id,
                    'partner_id': partner.id,
                    'date': delivery.delivery_route_id.route_id.date_next,
                    'origin': delivery.delivery_route_id.route_id.fleet_id.name + '-' + delivery.delivery_route_id.route_id.name,
                    'move_lines':(move_in_list if move_in_list else []),
                    'project_id': delivery.project_id.id,
                    'delivery_route_id': delivery.delivery_route_id.id,
                }
                picking_in_id = picking_obj.create(picking_in_vals)
                delivery.write({'picking_in_id': picking_in_id.id})
                [move_obj._action_explode_in(x) for x in picking_in_id.move_lines]
                picking_in_id.move_lines.action_confirm()
                picking_in_id.force_assign()
                picking_in_id.action_done()
        return True

    @api.multi
    def action_create_pickings(self):
        deliv_obj=self.env['delivery.propane']
        record_ids = self._context.get('active_ids')
        pickings = {}
        invoice_ids = []
        if record_ids:
            ctx = self._context.copy()
            ctx.update({'default_type': 'in_invoice', 'type': 'in_invoice'})
            for delivery in deliv_obj.browse(record_ids):
                if delivery.state not in ('done'):
                    partner = delivery.location_id or \
                        delivery.project_id and delivery.project_id.partner_id
                    new_key = "%s %s" % (str(partner.id), str(delivery.delivery_route_id.id))
                    if not new_key in pickings:
                        pickings[new_key] = []
                    pickings[new_key].append((delivery,delivery.delivery_date,delivery.delivery_route_id,delivery.product_id))
            for result in pickings.values():
                il = map(lambda x: x[3], result)
                deliveries = map(lambda x : x[0], result)
                self._make_picking(deliveries, il)
                invoice_ids.extend(self._make_invoices(deliveries, il))
            [rec.write({'state':'done'}) for rec in deliv_obj.browse(record_ids)]
            return {
                'name': 'Customer Invoices',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'domain': "[('id','in', ["+','.join(map(str,invoice_ids))+"])]",
                'context': "{'type':'out_invoice'}",
                }
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
