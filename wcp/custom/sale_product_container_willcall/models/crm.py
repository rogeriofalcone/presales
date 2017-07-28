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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class crm_phonecall(models.Model):
    _inherit = "crm.phonecall"

    willcall = fields.Boolean('Will Call', default=False)
    type = fields.Selection([
            ('willcall','Will Call'),
            ('sales','Sales Inquiry'),
            ('service','Service'),
            ('other','Other'),
        ], string='Type', default='willcall')

    @api.v7
    def action_phonecall_2_willcall(self, cr, uid, ids, context=None):
        if len(ids) != 1:
            raise except_orm(_('Warning!'),
                        _("It\'s only possible to convert one phonecall ata time."))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_product_container_willcall', 'analytic_willcall_view')
        return {
            'name': _('Create WillCall'),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'analytic.willcall',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
        }

class delivery_propane(models.Model):
    _inherit = "delivery.propane"

    phonecall_id = fields.Many2one('crm.phonecall', 'Logged Call')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
