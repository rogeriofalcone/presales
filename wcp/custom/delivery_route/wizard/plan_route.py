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

from openerp import models,api,fields
# from openerp.tools.translate import _

class plan_route(models.TransientModel):
    _name = 'plan.route'
    _description = 'Plan Route'

    route_id = fields.Many2one('delivery.route','Route Plan Template',
            required=True)
    route_instance_id = fields.Many2one('delivery.route.instance',
            'Route Instance')

    @api.v7
    def action_plan_route(self, cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids[0], context=context)
        delivery_line_obj = self.pool['account.analytic.delivery']
        delivery_propane_obj = self.pool['delivery.propane']
        plan_obj = self.pool['route.plan']
        plan_lines = []
        plan_search = [('route_id','=',rec.route_id.id)]
        if rec.route_instance_id:
            plan_search.append( ('route_instance_id','=',rec.route_instance_id.id))
            delivery_lines = delivery_propane_obj.search_read(cr, uid, [
                ('delivery_route_id','=',rec.route_id.id),
                ], ['sequence', 'partner_id'], context=context)
        else:
            delivery_lines = delivery_line_obj.search_read(cr, uid, [
                ('delivery_route_id','=',rec.route_id.id),
                ], ['sequence', 'location_id','numbercall'], context=context)

        locations = set([ v[0] for d in delivery_lines for k,v in d.items() \
                if k == 'location_id'])
        for line in delivery_lines:
            if line['location_id'][0] not in locations:
                continue
            locations.remove(line['location_id'][0])
            plan_line = {
                    'location_id': line['location_id'][0],
                    'sequence': line['sequence'],
                    'scheduled': line['numbercall'] and True or False,
                    }
            plan_lines.append((0,0,plan_line))
        plan = {
                'route_id': rec.route_id.id,
                'route_instance_id': rec.route_instance_id.id,
                'route_location_ids': plan_lines,
                }
        plan_search_ids = plan_obj.search(cr, uid, plan_search, context=context)
        if plan_search_ids:
            plan_obj.unlink(cr, uid, plan_search_ids, context=context)
        plan_id = self.pool['route.plan'].create(cr, uid, plan)
        return {
            'view_mode': 'form',
            'view_type': 'form,tree',
            'res_model': 'route.plan',
            'res_id': plan_id,
            'type': 'ir.actions.act_window',
            }

class route_plan(models.Model):
    _name = 'route.plan'
    _description = 'Route Plan'

    date = fields.Datetime('Date', default=fields.Datetime.now())
    route_id = fields.Many2one('delivery.route','Route Plan Template',
            required=True)
    route_instance_id = fields.Many2one('delivery.route.instance',
            'Route Instance')
    route_location_ids = fields.One2many('route.plan.location', 'route_plan_id',
            'Route Locations')

    @api.multi
    def write(self, values):
        if values.get('route_location_ids', False):
            location_obj = self.env['route.plan.location']
            sequence = 10
            for location_vals in values['route_location_ids']:
                location = location_obj.browse(location_vals[1])
                location_vals[2] = {
                        'sequence': sequence,
                        }
                if self.route_instance_id:
                    line_obj = self.env['delivery.propane']
                    lines = line_obj.search([
                        ('delivery_route_id','=',self.route_instance_id.id),
                        ('location_id','=',location.location_id.id),
                        ])
                    lines.write({'sequence': sequence})
                else:
                    line_obj = self.env['account.analytic.delivery']
                    lines = line_obj.search([
                        ('delivery_route_id','=',self.route_id.id),
                        ('location_id','=',location.location_id.id),
                        ])
                    lines.write({'sequence': sequence})
                sequence += 10

        return super(route_plan, self).write(values)

class route_plan_location(models.Model):
    _name = 'route.plan.location'
    _description = 'Route Plan Locations'
    _order = 'sequence'

    route_plan_id = fields.Many2one('route.plan','Route Plan',
            required=True, ondelete='cascade')
    location_id = fields.Many2one('res.partner', 'Location')
    sequence = fields.Integer('Sequence')
    scheduled = fields.Boolean('Scheduled')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
