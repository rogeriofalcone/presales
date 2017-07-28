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

from openerp import models, api

class product_product(models.Model):
    _inherit = 'product.product'

    @api.v7
    def need_procurement(self, cr, uid, ids, context=None):
        for product  in self.browse(cr, uid, ids, context=context):
            if product.container_ok:
                return False
        return super(product_product, self).need_procurement(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
