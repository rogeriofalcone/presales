# -*- coding: utf-8 -*-
from openerp import models, fields,api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime
from dateutil.relativedelta import relativedelta

class delivery_route(models.Model):
    _name = 'delivery.route'
    _description = 'Routes'

    name  = fields.Char('Route Name',required=True)
    start_date = fields.Date('Start Date', required=False)
    contact_per_id = fields.Many2one('hr.employee', 'Responsible')
    end_date = fields.Date('End Date', required=False)
    fleet_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    instance_ids = fields.One2many('delivery.route.instance', 'route_id',
            'Route Instances')
    delivery_lines = fields.One2many('account.analytic.delivery',
            'delivery_route_id', 'Delivery Schedule')
    interval_number = fields.Integer('Interval', required=True,
            default=1)
    sequence = fields.Integer('Sequence')
    interval_type = fields.Selection([
                        ('days','Days'),
                        ('weeks','Weeks'),
                        ('months','Months'),
            ], string='Interval Type', index=True, required=True,
            default='weeks', copy=False)
    date_next = fields.Datetime('Next Date')
    skip_weekends = fields.Boolean('Skip Weekends', default=True)

    """
    @api.onchange("interval_number","interval_type")
    def onchange_interval_num_type(self):
        self.date_next = datetime.datetime.now()+ \
            relativedelta(**{self.interval_type: self.interval_number})
    """

    @api.multi
    def create_instances(self):
        # context = self._context or {}
        instance_obj = self.env['delivery.route.instance']

        for route in self:
            instance_obj.search([
                ('route_id','=',route.id),
                ('state','=','draft'),
                ]).unlink()
            end_date = route.end_date
            today = datetime.strptime(fields.Datetime.now(self),DTF)
            start_date = datetime.strptime(route.date_next, DTF)
            if not end_date:
                end_date = start_date + \
                        relativedelta(years = 1)
            while start_date < end_date:
                if start_date >= today and \
                        (not route.skip_weekends or start_date.weekday() < 5):
                    route.write({'instance_ids': [(0, 0, {
                        'date': start_date.strftime(DTF),
                        'route_id': route.id,
                        'state': 'draft',
                        })]})
                start_date = start_date + \
                        relativedelta(**{route.interval_type: route.interval_number})
            route.write({'date_next': start_date.strftime(DTF)})

class delivery_route_instance(models.Model):
    _name = 'delivery.route.instance'
    _description = 'Route Instances'
    _order = 'date'
    _rec_name = 'route_id'

    date = fields.Datetime('Date', required=True)
    route_id = fields.Many2one('delivery.route', 'Fleet Assignment', required=True)
    fleet_id = fields.Many2one('fleet.vehicle', related='route_id.fleet_id')
    state = fields.Selection([
            ('draft','Future'),
            ('open','In Progress'),
            ('done','Done'),
            ('cancel','Cancelled'),
        ], string='Status', readonly=True, default='draft')

    @api.multi
    @api.depends('date', 'route_id')
    def name_get(self):
        result = []
        for instance in self:
            name = "[%s] %s" % (instance.date.split()[0], instance.route_id.name)
            result.append((instance.id, name))
        return result

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'done'})

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
                        ('partner_id','=',location.location_id.id),
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
