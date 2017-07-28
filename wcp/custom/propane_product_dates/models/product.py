# -*- encoding: utf-8 -*-

from datetime import datetime, timedelta
from openerp import models, fields, api

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def _get_date(self):
        dtype = False
        print dir(self)
        """Return a function to compute the limit date for this type"""
        duration = getattr(self.product_id, dtype)
        # set date to False when no expiry time specified on the product
        date = duration and (datetime.today()
                + timedelta(years=duration))
        return date and date.strftime('%Y-%m-%d %H:%M:%S') or False

    life_date = fields.Datetime('End of Life Date')
    last_recertification_date = fields.Datetime('Last Certification Date')
    next_recertification_date = fields.Datetime('Next Certification Date')
    removal_date = fields.Datetime('Removal Date')
    alert_date = fields.Datetime('Alert Date')
    manufacture_date = fields.Datetime('Manufacture Date')

    # Assign dates according to products data
    @api.multi
    def create(self, vals):
        newid = super(stock_production_lot, self).create(vals)
        towrite = []
        for f in ('life_date', 'next_recertification_date', 'removal_date', 'alert_date'):
            if not getattr(self, f):
                towrite.append(f)
        self.write(self.default_get(towrite))
        return newid

    @api.onchange('product_id')
    def _onchange_product(self):
        defaults = self.with_context(
            product_id=self.product_id.id).default_get(
                ['life_date', 'next_recertification_date', 'removal_date', 'alert_date'])
        for field, value in defaults.items():
            setattr(self, field, value)

class stock_quant(models.Model):
    _inherit = 'stock.quant'

    @api.v7
    def _get_quants(self, cr, uid, ids, context=None):
        return self.pool.get('stock.quant').search(cr, uid, [('lot_id', 'in', ids)], context=context)

    removal_date = fields.Datetime(string='Removal Date',
                    related='lot_id.removal_date',store=True)

    @api.v7
    def apply_removal_strategy(self, cr, uid, location, product, qty, domain, removal_strategy, context=None):
        if removal_strategy == 'fefo':
            order = 'removal_date, location_id, package_id, lot_id, in_date, id'
            return self._quants_get_order(cr, uid, location, product, qty, domain, order, context=context)
        return super(stock_quant, self).apply_removal_strategy(cr, uid, location, product, qty, domain, removal_strategy, context=context)


class product_product(models.Model):
    _inherit = 'product.template'

    life_time = fields.Integer('Product Life Time')
    recertification_time = fields.Integer('Recertification Years')
    removal_time = fields.Integer('Removal Time')
    alert_time = fields.Integer('Product Alert Time')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
