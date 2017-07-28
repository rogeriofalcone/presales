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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta

_intervalTypes = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
}

class analytic_service_call_location(osv.osv):
    _inherit = 'analytic.service.call.location'

    def _get_sched_contracts(self, cr, uid, ids, context=None):
        cr.execute("""SELECT l.* FROM analytic_service_call_location l
                      JOIN account_analytic_account a
                      ON l.account_id = a.id
                      WHERE l.numbercall != 0
                      AND a.state = 'open'
                      AND l.active AND l.nextcall <= (now() at time zone 'UTC' + a.sc_offset * interval '1 day' );
                      """, )
        locations = cr.dictfetchall()
        return locations

    def update_next_fields(self, cr, uid, location_dict, context=None):
        location = self.browse(cr, uid, location_dict['id'], context=context)
        vals = {}
        if location.numbercall == 0:
            vals['active'] = False
        else:
            if location.numbercall > 0:
                vals['numbercall'] = location.numbercall - 1
            vals['nextcall'] = (datetime.strptime(location.nextcall, DEFAULT_SERVER_DATETIME_FORMAT) +\
                    _intervalTypes[location.interval_type](location.interval_number)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return self.write(cr, uid, [location.id], vals, context=context)

    def get_default_values(self, cr, uid, location_dict, context=None):
        partner_obj = self.pool.get('res.partner')
        location = self.browse(cr, uid, location_dict['id'], context=context)
        contract = location.account_id
        if not contract.partner_id:
            return False
        no_sales_order = False
        if contract.contract_type == 'prepaid':
            no_sales_order = True
        partner = contract.partner_id
        partner_addr = partner_obj.address_get(cr, uid, [partner.id], ['invoice', 'contact', 'delivery'])
        pricelist = partner.property_product_pricelist.id
        return {
                'sc_name': 'CONTRACT PMP: %s' % contract.name,
                'sc_description': 'Scheduled Preventative Maintenance\n%s' % contract.sc_description,
                'partner_id': partner.id,
                'partner_address_id': location.location_id and location.location_id.id,
                'partner_invoice_id': partner_addr['invoice'],
                'partner_contact_id': partner_addr['contact'],
                'partner_shipping_id': partner_addr['delivery'],
                'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'pricelist_id': pricelist,
                'note': contract.description,
                'no_sales_order': no_sales_order,
                'client_order_ref': contract.client_order_ref,
                'notes': contract.notes,
                }

    def get_default_lines(self, cr, uid, location_dict, context=None):
        if context is None:
            context = {}
        so_line_obj = self.pool.get('sale.order.line')
        location = self.browse(cr, uid, location_dict['id'], context=context)
        res = []
        for line in location.account_id.sc_invoice_line_ids:
            if line.product_id:
                product = line.product_id
                tax = self.pool.get('account.fiscal.position').map_tax(cr, uid, False, product.taxes_id)
                pricelist = line.analytic_account_id.partner_id.property_product_pricelist and \
                        line.analytic_account_id.partner_id.property_product_pricelist.id or False
                so_line = so_line_obj.product_id_change(cr, uid, [product.id], pricelist,
                        product.id, line.quantity, line.uom_id.id, qty_uos=False, uos=False, name=False,
                        partner_id=line.analytic_account_id.partner_id.id, lang=False, update_tax=True, date_order=False, context=context)['value']
                so_line.update(name=line.name,product_uom=line.uom_id.id,product_id=product.id,product_uom_qty=line.quantity,tax_id=[(6, 0, tax)],price_unit=line.price_unit)
            else:
                so_line = {
                    'name': line.name or '/',
                    }
            res.append((0,0,so_line))
        return res

    def create_sale_order(self, cr, uid, sc_data, sc_id, context=None):
        so_obj = self.pool.get('sale.order')
        sc_data.update(sc_id=sc_id)
        return so_obj.create(cr, uid, sc_data, context=context)

    def create_service_call(self, cr, uid, sc_data, location_dict, context=None):
        sc_data_new = sc_data.copy()
        sc_obj = self.pool.get('service')
        sc_data_new['name'] = sc_data_new.pop('sc_name')
        sc_data_new['description'] = sc_data_new.pop('sc_description')
        sc_data_new['date'] = location_dict.get('nextcall')
        sc_data_new.update(type='normal',contract=True,duration=1.5,estimated=True,user_id=False)
        sc_id = sc_obj.create(cr, uid, sc_data_new,context=context)
        return sc_id

    def sched_service_calls(self, cr, uid, ids, context=None):
        sc_obj = self.pool.get('service')
        if context is None:
            context = {}
        locations = self._get_sched_contracts(cr, uid, ids, context=context)
        for location_dict in locations:
            sc_data = self.get_default_values(cr, uid, location_dict, context=context)
            if not sc_data:
                continue
            sc_id = self.create_service_call(cr, uid, sc_data, location_dict, context=context)
            account_id = sc_obj.create_analytic_account(cr, uid, sc_id, location_dict['account_id'])
            contract = self.pool.get('account.analytic.account').browse(cr, uid, location_dict['account_id'])
            if contract.contract_type != 'prepaid':
                sc_data.update(project_id=account_id)
                sc_data['order_line'] = self.get_default_lines(cr, uid, location_dict, context=context)
                sale_order_id = self.create_sale_order(cr, uid, sc_data, sc_id, context=context)
                sc_obj.write(cr, uid, [sc_id], {'sale_order_id': sale_order_id})
            self.update_next_fields(cr, uid, location_dict, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
