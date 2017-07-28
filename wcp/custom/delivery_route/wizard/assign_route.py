from openerp import models,api,fields

class assign_route(models.TransientModel):
    _name = 'assign.route'
    _description = 'Assign Route'

    delivery_route_id = fields.Many2one('delivery.route','Route')

    @api.multi
    def assign_route_delivery(self):
        acc_deliv_obj=self.env['account.analytic.delivery']
        active_ids = self._context.get('active_ids')
        for act in acc_deliv_obj.browse(active_ids):
            act.write({'delivery_route_id':self.delivery_route_id.id})
        return True
