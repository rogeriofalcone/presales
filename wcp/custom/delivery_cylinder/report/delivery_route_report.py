# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.report import report_sxw

class routedelivery(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(routedelivery, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
            'get_locations': self._get_location_deliveries,
            'get_route': self._get_route,
            'get_summary_products': self._get_summary_products,
            'get_detail_products': self._get_detail_products,
            'get_pickings': self._get_pickings,
        })

    def _get_route_instance(self, form):
        if form.get('route_instance_id', False):
            return form['route_instance_id'][0]
        return False

    def _get_route(self, form):
#        Returns the name,responsible employee,vehicle from the route associated with 
#        the route instance and the date from the route instance
        res = {
                'route': False,
                'vehicle': False,
                'user_id': False,
                'date': False,
                }
        route_instance_id = self._get_route_instance(form)
        route_instance = self.pool['delivery.route.instance'].browse(self.cr,
                self.uid, route_instance_id)
        if route_instance.route_id:
            res.update(
                route = route_instance.route_id.name,
                vehicle = route_instance.fleet_id.name,
                user_id = route_instance.route_id.contact_per_id.name,
                date = route_instance.date,
                )
        return res

    def _get_deliveries(self, location):
        delivery_obj = self.pool['delivery.propane']
        delivery_ids = delivery_obj.search(self.cr, self.uid, [
            '|',('location_id','=',location.id),
            ('project_id.partner_id','=',location.id),
            ('state','=','draft'),
            ])
        deliveries = delivery_obj.browse(self.cr, self.uid,
                delivery_ids)
        return deliveries

    def _get_pickings(self, form):
        picking_obj = self.pool['stock.picking']
        route_instance_id = self._get_route_instance(form)
        route_instance = self.pool['delivery.route.instance'].browse(self.cr,
                self.uid, route_instance_id)
        picking_ids = picking_obj.search(self.cr, self.uid, [
            '|',('delivery_route_id','=',route_instance.id),
            ('route_id','=',route_instance.route_id.id),
            ('state','not in',['cancel','done']),
            ])
        pickings = picking_obj.browse(self.cr, self.uid,
                picking_ids)
        return pickings

    def _get_location_deliveries(self, form):
        delivery_obj = self.pool['delivery.propane']
        route_instance_id = False
        res = {}
        route_instance_id = self._get_route_instance(form)
        locations = delivery_obj.get_instance_locations(self.cr, self.uid,
                [], route_instance_id=route_instance_id)
        for location in locations:
            deliveries = self._get_deliveries(location)
            res[location] = [(x.product_id.name, x.schedule_in, x.schedule_out)
                    for x in deliveries]
        return res

    def _get_detail_products(self, location):
        return self._get_deliveries(location)
    
    def _get_summary_products(self, form):
        res = []
        result = {}
        all_products = self._get_location_deliveries(form)
        [res.extend(v) for k, v in all_products.items()]
        for product, qty_in, qty_out in res:
            result[product] = (result.get(product, [0,0])[0] + qty_in,
                    result.get(product, [0,0]) [0] + qty_out)
        return [(k, v[0], v[1]) for k, v in result.items()]

class report_route_delivery(osv.AbstractModel):
    _name = 'report.delivery_cylinder.report_route_delivery'
    _inherit = 'report.abstract_report'
    _template = 'delivery_cylinder.report_route_delivery'
    _wrapped_report_class = routedelivery

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
