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

class Sale_Order_Line(models.Model):
    _inherit = "sale.order.line"
    
    image=fields.Binary("Image")
    
    @api.one
    def write(self,vals):
        res=super(Sale_Order_Line,self).write(vals)
        prodict={}
        if vals.get('product_id'):
            custom_attr=""
            for value in [line.value.name for line in self.product_attributes 
            if line.attribute.is_custom]:
                custom_attr+=value
            prodict['text_attribute']=custom_attr
            prodict['partner_id']=self.order_id.partner_id.id
            if self.image:
                prodict['image_variant']=self.image
            self.product_id.write(prodict)
    
Sale_Order_Line()
    





