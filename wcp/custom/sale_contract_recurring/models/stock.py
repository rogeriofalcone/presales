# -*- coding: utf-8 -*-
from dateutil import relativedelta
from openerp import models, api,fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_location_path(models.Model):
    _inherit = 'stock.location.path'

    @api.v7
#    for incoming shipment set end date as a schedule date
    def _prepare_push_apply(self, cr, uid, rule, move, context=None):
        newdate = (datetime.strptime(move.date_expected, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta.relativedelta(days=rule.delay or 0)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return {
                'origin': move.origin or move.picking_id.name or "/",
                'location_id': move.location_dest_id.id,
                'location_dest_id': rule.location_dest_id.id,
                'date': newdate,
                'company_id': rule.company_id and rule.company_id.id or False,
                'date_expected': move.procurement_id.sale_line_id.end_date or newdate,
                'picking_id': False,
                'picking_type_id': rule.picking_type_id and rule.picking_type_id.id or False,
                'propagate': rule.propagate,
                'push_rule_id': rule.id,
                'warehouse_id': rule.warehouse_id and rule.warehouse_id.id or False,
            }
stock_location_path()

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('account.analytic.account',string='Project')

    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
        op_obj = self.pool['stock.pack.operation']
        res=super(stock_picking,self).do_transfer(cr,uid,picking_ids)
        for pick in self.browse(cr,uid,picking_ids):
            project_id=pick.sale_id.project_id
            op_ids = op_obj.search(cr, uid, [
                    ('picking_id', '=', pick.id),
                    ])
            op = op_obj.browse(cr, uid, op_ids, context=context)
            lot_ids = [x.lot_id.id for x in op]
            for rental_line in project_id.rental_product_line_ids:
                if rental_line.sale_id==pick.sale_id:
                    rental_line.write({'date_end':pick.min_date})
                    #FIXME: Really clumsy way to do it...
                    product_ids = [x.product_id.id for x in pick.move_lines]
                    if rental_line.product_id.id in product_ids:
                        if not rental_line.lot_id:
                            rental_line.write({'lot_id': lot_ids.pop(0)})
                        else:
                            rental_line.write({
                                'date_end': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                })
                            lot_ids.pop(0)
        return res
stock_picking()

class stock_move(models.Model):
    _inherit = 'stock.move'

#    Override for add project value in stock.picking object

    @api.v7
    def _prepare_picking_assign(self, cr, uid, move, context=None):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited.
        """
        sale_obj = self.pool.get('sale.order')
        sale_id=sale_obj.search(cr,uid,[('name','=',move.group_id.name)],
            limit=1)
        project_id = False
        if sale_id:
            project_id=sale_obj.browse(cr,uid,sale_id).project_id.id
        values = {
            'origin': move.origin,
            'company_id': move.company_id and move.company_id.id or False,
            'move_type': move.group_id and move.group_id.move_type or 'direct',
            'partner_id': move.partner_id.id or False,
            'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
            'project_id': project_id or False,
            }
        return values

    
