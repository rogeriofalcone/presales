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

from openerp import models, api, fields, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm
from datetime import datetime
import base64
from StringIO import StringIO

class delivery_load_midcom(models.TransientModel):
    _name = 'delivery.load.midcom'
    _description = 'Load MID:COM Deliveries'

    delivery_route_id = fields.Many2one('delivery.route','Route')
    midcom_file = fields.Binary('File')

    @api.multi
    def action_load_midcom(self):
        if not self.midcom_file:
            return False
        midcom_file = StringIO(base64.b64decode(self.midcom_file))
        analytic_obj = self.env['account.analytic.account']
        for line in midcom_file:
            fmt_quantity = line[252:259].replace(" ", "").replace("-","")
            quantity = fmt_quantity and float(fmt_quantity) or 0.0
            if quantity:
                analytic = analytic_obj.search([('code','=',line[68:73])])
                product = self.env['product.product'].search([('name','=','Propane Home Heating')])
                if not analytic:
                    raise except_orm(_('Error!'),
                        _("No Customer Account found for %s") % (line[68:73],))
                res = {
                        'actual_out': quantity,
                        'project_id': analytic.id,
                        'partner_id': analytic.partner_id and analytic.partner_id.id,
                        'delivery_route_id': self.delivery_route_id.id,
                        'delivery_date': datetime.strptime(line[213:222],
                            '%H%M%m%d%y').strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'product_id': product.id,
                        }
                self.env['delivery.propane'].create(res)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
