from openerp import models, fields

class account_asset_asset(models.Model):
    
    _inherit='account.asset.asset'
    
    serial_no = fields.Many2one('stock.production.lot', 'Serial No.')
    quant = fields.Many2one('stock.quant', 'Quant')