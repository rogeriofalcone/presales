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
from openerp import models,fields,api,_

class product_attribute_value(models.Model):
    _inherit="product.attribute.value"
    
    @api.model
    def default_get(self,fields):
        context=self._context
        res=super(product_attribute_value,self).default_get(fields)
        attribute=context.get('attribute') or False
        if attribute:
            res.update({'attribute_id':attribute})
        return res
    
    @api.multi
    def name_get(self):
        context=self._context
        if context and not context.get('show_attribute', True):
            return super(product_attribute_value, self).name_get()
        res = []
        for value in self:
            res.append([value.id, "%s: %s" % (value.attribute_id.name, 
            value.name[:20])])
        return res
        
    
product_attribute_value()

class product_attribute(models.Model):
    _inherit="product.attribute"
    
    is_custom=fields.Boolean(string="Is Custom")
    
product_attribute()

class mrp_production(models.Model):
    _inherit="mrp.production"
    
    image=fields.Binary("Image")
mrp_production()

class procurement_order(models.Model):
    _inherit="procurement.order"
    
    @api.model
    def _prepare_mo_vals(self,procurement):
        vals=super(procurement_order,self)._prepare_mo_vals(procurement)
        origin=vals['origin'].split(':',1)[0]
        so_id=self.env['sale.order'].search([('name','=',origin)])
        for line in so_id.order_line:
            if procurement.product_id.id==line.product_id.id:
                vals['image']=line.image
        return vals
    
procurement_order()


class product_product(models.Model):
    _inherit="product.product"
    
    text_attribute=fields.Text("Text Attribute")
    partner_id=fields.Many2one('res.partner','Customer')
    
product_product()
