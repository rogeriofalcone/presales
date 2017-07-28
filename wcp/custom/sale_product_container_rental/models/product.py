# -*- encoding: utf-8 -*-

from openerp import models, fields

class product_template(models.Model):
    _inherit = 'product.template'

    default_interval_type = fields.Selection([
        ('month','Month'),
        ('year','Year')],
        'Interval Type', required=True, default='month')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
