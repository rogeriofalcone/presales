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

'''
from openerp import models

class PartnerCode(models.Model):
    _inherit = "res.partner"

    def name_get(self, cr, uid, ids, context=None):
        res = super(PartnerCode, self).name_get(cr, uid, ids, context=None)
        for idx, partner_id in enumerate(res):
            for record in self.browse(cr, uid, partner_id[0], context=context):
                if not record.parent_id and record.is_company and record.ref:
                    res[idx] = (record.id, "[%s] %s" % (record.ref, record.name))
        return res
'''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
