from openerp import models, fields

class product_template(models.Model):
    _inherit = 'product.template'
    
    asset_categ = fields.Many2one('account.asset.category', 'Asset Category')