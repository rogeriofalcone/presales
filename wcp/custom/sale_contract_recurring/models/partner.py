# -*- coding: utf-8 -*-
from openerp import models, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    property_stock_customer_rental = fields.Many2one('stock.location',
        'Tank Rental Location',company_dependent=True)
