# -*- encoding: utf-8 -*-

from openerp import models, fields

class account_analytic_product_rental(models.Model):
    _inherit = 'account.analytic.product.rental'

    last_recertification_date = fields.Datetime(string='Last Recertification Date',
                    related='lot_id.last_recertification_date',store=True)
    next_recertification_date = fields.Datetime(string='Next Recertification Date',
                    related='lot_id.next_recertification_date',store=True)
    manufacture_date = fields.Datetime(string='Manufacture Date',
                    related='lot_id.manufacture_date',store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
