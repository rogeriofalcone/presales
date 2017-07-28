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

from openerp import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

    rental_ok = fields.Boolean('Rental Product')
    rental_price = fields.Float('Rental Price')
    waiver_pct = fields.Float('Waiver Fee %')

    @api.onchange("rental_ok")
    def onchange_rental(self):
        route_tank_ids=self.env['stock.location.route'].search(
            [('name','=','Rental Product')],limit=1)
        route_cylinder_ids=self.env['stock.location.route'].search(
            [('name','=','Cylinder')],limit=1)
        if not self.rental_ok and self.container_ok:
            route_id = [route_cylinder_ids.id]
            track_all = False
        if not self.rental_ok and not self.container_ok:
            route_id=[]
            track_all = False
        if self.rental_ok and self.container_ok:
            route_id=[]
            track_all = False
        if self.rental_ok and not self.container_ok:
            if route_tank_ids:
                route_id = [route_tank_ids.id]
                track_all = True
        self.route_ids = [(6,0,route_id)]
        self.track_all = track_all

    @api.onchange("container_ok")
    def onchange_container(self):
        route_cylinder_ids=self.env['stock.location.route'].search(
            [('name','=','Cylinder')],limit=1)
        route_tank_ids=self.env['stock.location.route'].search(
            [('name','=','Rental Product')],limit=1)
        if not self.container_ok and self.rental_ok:
            route_id = [route_tank_ids.id]
            track_all = True
        if self.container_ok and self.rental_ok:
            route_id = []
            track_all = False
        if not self.rental_ok and not self.container_ok:
            route_id=[]
            track_all = False
        if self.container_ok and not self.rental_ok:
            if route_cylinder_ids:
                route_id = [route_cylinder_ids.id]
                track_all = False
        self.route_ids = [(6,0,route_id)]
        self.track_all = track_all

class product_product(models.Model):
    _inherit = 'product.product'

    @api.onchange("rental_ok")
    def onchange_rental(self):
        route_tank_ids=self.env['stock.location.route'].search(
            [('name','=','Rental Product')],limit=1)
        route_cylinder_ids=self.env['stock.location.route'].search(
            [('name','=','Cylinder')],limit=1)
        if not self.rental_ok and self.container_ok:
            route_id = [route_cylinder_ids.id]
            track_all = False
        if not self.rental_ok and not self.container_ok:
            route_id=[]
            track_all = False
        if self.rental_ok and self.container_ok:
            route_id=[]
            track_all = False
        if self.rental_ok and not self.container_ok:
            if route_tank_ids:
                route_id = [route_tank_ids.id]
                track_all = True
        self.route_ids = [(6,0,route_id)]
        self.track_all = track_all

    @api.onchange("container_ok")
    def onchange_container(self):
        route_cylinder_ids=self.env['stock.location.route'].search(
            [('name','=','Cylinder')],limit=1)
        route_tank_ids=self.env['stock.location.route'].search(
            [('name','=','Rental Product')],limit=1)
        if not self.container_ok and self.rental_ok:
            route_id = [route_tank_ids.id]
            track_all = True
        if self.container_ok and self.rental_ok:
            route_id = []
            track_all = False
        if not self.rental_ok and not self.container_ok:
            route_id=[]
            track_all = False
        if self.container_ok and not self.rental_ok:
            if route_cylinder_ids:
                route_id = [route_cylinder_ids.id]
                track_all = False
        self.route_ids = [(6,0,route_id)]
        self.track_all = track_all

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
