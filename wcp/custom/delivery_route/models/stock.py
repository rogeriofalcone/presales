# -*- coding: utf-8 -*-
from openerp import models, fields


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    delivery_route_id = fields.Many2one('delivery.route.instance','Route Instance')
    route_id = fields.Many2one('delivery.route','Route')
    picking_type_code = fields.Selection(related='picking_type_id.code', string='Type')
