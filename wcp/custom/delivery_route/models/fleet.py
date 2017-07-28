# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class fleet_vehicle(osv.Model):
    _inherit = 'fleet.vehicle'

    def _new_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        print ids
        for record in self.browse(cr, uid, ids, context=context):
            print record
            res[record.id] = record.license_plate

    _columns = {
            'name': fields.function(_new_name_get_fnc, type="char", string='Name', store=True),
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
