# -*- encoding: utf-8 -*-

from openerp import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    rental_location_code = fields.Char('Location Code')

    @api.model
    def create(self, vals):
        if not vals.get('rental_location_code', False) and \
                vals.get('parent_id', False) and \
                vals.get('type', False) == 'delivery':
            def try_int(x):
                try:
                    return int(x)
                except ValueError:
                    return False
            self.search([
                ('parent_id','=',self.parent_id.id),
                ('type','=','delivery'),
                ])
        return super(res_partner, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
