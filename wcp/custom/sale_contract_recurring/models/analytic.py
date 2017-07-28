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

from openerp import models,fields,api,_
from openerp.exceptions import except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp
from datetime import datetime


class account_analytic_invoice_line(models.Model):
    _inherit = "account.analytic.invoice.line"

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    intervals = fields.Integer(string='Interval')
    last_invoice_date = fields.Date(string='Last Invoice Date')

class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    property_stock_customer_rental = fields.Many2one('stock.location', string='Rental Location',
        related='partner_id.property_stock_customer_rental')
    total_qty = fields.Float(string='Total Products Onsite',digits=dp.get_precision('Account'),
         readonly=True, compute='_compute_qty', track_visibility='always')

    @api.multi
    def get_rental_product_by_date(self, product_ids, states, invoice_date=False):
        self._cr.execute("""
            SELECT product_id,
                SUM(
                    CASE WHEN location_id = %s
                        THEN -product_uom_qty
                        ELSE product_uom_qty
                    END)
            FROM stock_move
            WHERE (location_id = %s
            OR location_dest_id = %s)
            AND product_id IN %s
            AND date < %s
            AND state IN %s
            GROUP BY product_id""", (self.property_stock_customer_rental.id,
                self.property_stock_customer_rental.id, self.property_stock_customer_rental.id,
                tuple(product_ids.ids), invoice_date, states))

        return self._cr.fetchall()

    @api.multi
    def get_product_invoice_count(self, last_invoice_date=False, invoice_date=False):
        last_invoice_date = last_invoice_date or self.rental_lastcall
        invoice_date = invoice_date or fields.Date.context_today(self)
        total_days = (datetime.strptime(invoice_date, DEFAULT_SERVER_DATE_FORMAT) \
                - datetime.strptime(last_invoice_date,
                        DEFAULT_SERVER_DATE_FORMAT)).days
        product_obj = self.env['product.product']
        product_ids = product_obj.search([('rental_ok','=',True)])
        states = ('done',)
        starting_count = self.get_rental_product_by_date(product_ids, states, last_invoice_date)
        self._cr.execute('''
            SELECT product_id,
                CASE WHEN location_id = %s
                    THEN -product_uom_qty
                    ELSE product_uom_qty
                END * (%s - date::timestamp::date) AS quantity
            FROM stock_move
            WHERE (location_id = %s
            OR location_dest_id = %s)
            AND product_id IN %s
            AND date >= %s
            AND date <= %s
            AND state IN %s
            GROUP BY product_id, date, location_id, location_dest_id, product_uom_qty
            ORDER BY date asc''', (self.property_stock_customer_rental.id, invoice_date,
                self.property_stock_customer_rental.id, self.property_stock_customer_rental.id,
                tuple(product_ids.ids), last_invoice_date, invoice_date + ' 23:59:59',
                states))
        res = self._cr.dictfetchall()
        for item in starting_count:
            if item[0] in res:
                res[item[0]] += item[1] * total_days
            else:
                res[item[0]] = item[1] * total_days
        return res

    def _prepare_invoice_lines(self, product_id, qty):
        product = self.env['product.product'].browse(product_id)
        account_id = product.property_account_income.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ.id
        if not account_id:
            raise except_orm(_('Error!'),
                _('Please define income account for this product: "%s" (id:%d).') % \
                                            (product.name, product.id,))
        #TODO: get price off rental lines
        #TODO: proper UOM handling
        return (0, 0, {
                'account_analytic_id': self.id,
                'partner_id': self.partner_id.id,
                'product_id': product_id,
                'account_id': account_id,
                'name': product.name,
                'quantity': qty,
                'price_unit': product.rental_price,
                'uos_id': product.uom_id.id,
                'invoice_line_tax_id': [(6, 0, product.taxes_id.ids)],
                })

    def _prepare_invoice(self):
        #TODO: Needs to get the correct name, origin, etc
        return {
            'name': 'Test Invoice',
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable.id,
            'partner_id': self.partner_id.id,
            'journal_id': self.env['account.invoice'].default_get(
                                                ['journal_id'])['journal_id'],
            }

    @api.multi
    def manual_invoice(self):
        '''
        Creates manual invoice for rental products
        '''
        mod_obj = self.env['ir.model.data']
        invoice = {}
        invoice_date = fields.Date.context_today(self)
        if invoice_date <= self.rental_lastcall:
            raise except_orm(_('Error!'),_("Nothing to invoice"))
        #TODO: return if raw_lines is none
        raw_lines =  self.get_product_invoice_count(self.rental_lastcall,
                fields.Date.context_today(self))
        invoice = self._prepare_invoice()
        invoice.update(
                invoice_line = [self._prepare_invoice_lines(x['product_id'],
                                            x['quantity']) for x in raw_lines],
                date_invoice = invoice_date
                )
        invoice_id = self.env['account.invoice'].create(invoice)
        self.rental_lastcall = invoice_date
        res = mod_obj.get_object_reference('account', 'invoice_form')
        res_id = res and res[1] or False
        return {
            'name': _('Customer Invoices'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': invoice_id.id,
            }

    @api.v7
    def _get_product_context(self, cr, uid, ids, context=None):
        context = context or {}
        rec = self.browse(cr, uid, ids[0], context=context)
        product_ids = [context.get('product_id')] or \
            self.pool['product.product'].search(cr, uid,[
                ('rental_ok','=',True)
                ], context=context)
        if not context.get('location'):
            context.update(
                    location = rec.property_stock_customer_rental.id,
                    search_default_real_stock_available = 1,
                    search_default_virtual_stock_available = 1,
                    search_default_virtual_stock_negative = 1,
                    search_default_real_stock_negative = 1)
        if not product_ids or not context.get('location', False):
            return False
        return context

    @api.v7
    def action_view_rental_products(self, cr, uid, ids, context=None):
        '''
        This function returns an action that displays the rental products at the
        customer location
        '''
        return {
            'name': _('Rental Products'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': self._get_product_context(cr, uid, ids, context=context),
            'domain': "[('rental_ok','=',True)]",
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            }

    @api.one
    def _compute_qty(self):
        picking_obj = self.env['stock.picking']
        pick_ids = []
        pick_in_ids = []
        picking_out_ids=picking_obj.search([('project_id','=',self.id),('state','=','done'),('picking_type_id.code','=','outgoing')])
        picking_in_ids=picking_obj.search([('project_id','=',self.id),('state','=','done'),('picking_type_id.code','=','incoming')])
        pick_ids += [picking.move_lines for picking in picking_out_ids]
        pick_in_ids += [picking.move_lines for picking in picking_in_ids]
        qtyout=sum([sum([(mv.product_uom_qty) for mv in move]) for move in pick_ids])
        qtyin=sum([sum([(mv.product_uom_qty) for mv in move]) for move in pick_in_ids])
        self.total_qty = qtyout-qtyin

    @api.multi
    def action_view_delivery(self):
        picking_obj = self.env['stock.picking']
        picking_ids=picking_obj.search([('project_id','=',self.id)])
        return {
            'name': _('Stock Picking'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': str([('id', 'in', [pic.id for pic in picking_ids])]),
        }


class account_analytic_delivery(models.Model):
    _inherit = 'account.analytic.delivery'

    product_id = fields.Many2one('product.product','Product')
    quantity = fields.Float('Quantity')
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')
    sale_id = fields.Many2one('sale.order', string='Sale Order',
        related='sale_line_id.order_id',store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
