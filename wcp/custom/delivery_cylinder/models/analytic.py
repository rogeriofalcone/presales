# -*- coding: utf-8 -*-
from openerp import models,api,fields
# import datetime
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
# from dateutil.relativedelta import relativedelta


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    def _create_cust_deliveries(self, cust_delivery, instance):
        cylinder_obj = self.env['delivery.propane']
        cylinder_vals = {
            'sequence': cust_delivery.sequence,
            'product_id': cust_delivery.product_id.id,
            'schedule_in': cust_delivery.quantity,
            'schedule_out': cust_delivery.quantity,
            'actual_in': cust_delivery.quantity,
            'actual_out': cust_delivery.quantity,
            'delivery_date': instance.date,
            'location_id': cust_delivery.location_id.partner_id.id,
            'project_id': cust_delivery.account_id.id,
            'delivery_route_id': instance.id,
            'price_unit': cust_delivery.sale_line_id.price_unit,
            'type': 'cylinder',
        }
        return cylinder_obj.create(cylinder_vals)

    def _get_cust_deliveries(self,instance):
        cust_delivery_obj = self.env['account.analytic.delivery']
        cylinder_obj = self.env['delivery.propane']
        cust_delivery_ids = cust_delivery_obj.search([
                ('delivery_route_id','=',instance.route_id.id),
                ('date_start','<=',instance.date),
                '|',('date_end','>=',instance.date),
                ('date_end','=',False),
                ])
        for cust_delivery in cust_delivery_ids:
            # We already have a delivery for this, so skip
            #TODO: need to do the interval alignment a little better
            if cylinder_obj.search([
                ('product_id','=',cust_delivery.product_id.id),
                ('delivery_date','=',instance.date),
                ('location_id','=',instance.date),
                ('delivery_route_id','=',instance.id),
                ]):
                continue
            if cust_delivery.skip_interval > 1:
                cust_delivery.skip_interval -= 1
                continue
            self._create_cust_deliveries(cust_delivery,instance)
            cust_delivery.skip_interval = cust_delivery.interval_number
        return True

    @api.multi
    def sched_delivery_cylinder_calls(self, route=False, date=False):
        instance_obj = self.env['delivery.route.instance']
        date = fields.Date.context_today(self)
        search = [('state','=','draft')]
        if route:
            search.append(('route_id','=',route.id))
        if date:
            search.append(('date', '<=', date))
        instance_ids = instance_obj.search(search)
        for instance in instance_ids:
            self._get_cust_deliveries(instance)
        return True

#    Invoice create for rental lines
    @api.multi
    def _make_invoices(self, rentals, ln):
        invoice_obj=self.env['account.invoice']
        line_obj=self.env['account.invoice.line']
        invoice_vals = {}
        invoice_line_list = []
        for rental in rentals:
            for line in ln:
                val = line_obj.product_id_change(rental.product_id.id, False,partner_id=rental.partner_id.id, fposition_id=False)
                res = val['value']
                invoice_line_vals={
                        'name': rental.product_id.description_sale or line.name,
                        'product_id': rental.product_id.id,
                        'uos_id': rental.product_id.uom_id.id,
                        'account_id':rental.product_id.categ_id.property_account_income_categ.id or rental.product_id.property_account_income.id,
                        'quantity':rental.quantity,
                        'price_unit':rental.price_unit,
                        'partner_id':rental.partner_id.id,
                        'invoice_line_tax_id':[(6, 0, res.get('invoice_line_tax_id'))],
                        'account_analytic_id':rental.analytic_account_id.id

                    }
                invoice_line_list.append((0,0,invoice_line_vals))
        if invoice_line_list:
            invoice_vals = {
                'partner_id': rental.analytic_account_id.partner_id.id,
                'date_invoice': rental.nextcall,
                'origin': rental.analytic_account_id.name,
                'invoice_line':(invoice_line_list if invoice_line_list else []),
                'account_id': rental.analytic_account_id.partner_id.property_account_receivable.id,
            }
            invoice_obj.create(invoice_vals)
        return True

    @api.multi
    def sched_rental_line_calls(self):
        rental_obj=self.env['account.analytic.product.rental']
        date = fields.Date.context_today(self)
        rental_ids=rental_obj.search([('nextcall','>=',date),('nextcall','<=',date)])
        if rental_ids:
            rental_line = {}
            for line in rental_ids:
                new_key=str(line.location_id.id)+' '+line.nextcall+' '+str(line.analytic_account_id.id)
                if not new_key in rental_line:
                    rental_line[new_key] = []
                rental_line[new_key].append((line,line.nextcall,line.product_id))
            res = []
            for result in rental_line.values():
                il = map(lambda x: x[2], result)
                rentals = map(lambda x : x[0], result)
                res.append(self._make_invoices(rentals, il))
        return True
