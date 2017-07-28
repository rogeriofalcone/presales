from openerp import models, fields,api,_

class stock_quant(models.Model):
    _inherit="stock.quant"
    
    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, force_location_from=False, force_location_to=False, context=None):
        asses_vals = {}
        asset_obj = self.pool.get('account.asset.asset')
        quant = super(stock_quant, self)._quant_create(cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=force_location_from, force_location_to=force_location_to, context=context)
        #condition checking if product has an asset category and is a receipt from supplier to create an asset
        if move.product_id.valuation == 'real_time' and move.product_id.asset_categ and move.location_id.usage == 'supplier':
            asset_vals = {
                'name' : move.product_id.name,
                'serial_no' : lot_id or False,
                'parent_id' : move.product_id.asset_categ.parent_id.id,
                'type' : 'normal',
                'company_id' : move.product_id.company_id.id,
                'purchase_value': move.price_unit,
                'category_id': move.product_id.asset_categ.id,
                'method_time' : move.product_id.asset_categ.method_time,
                'method_number' : move.product_id.asset_categ.method_number,
                'method_period' : move.product_id.asset_categ.method_period,
                'quant' : quant.id,
                          }
            #creating an asset
            asset_id = asset_obj.create(cr,uid,asset_vals, context=context)
            #confirming asset
            asset_obj.validate(cr,uid,asset_id,context=None)
        return quant
    
    
    def move_quants_write(self, cr, uid, quants, move, location_dest_id, dest_package_id, context=None):
        asset_obj = self.pool.get('account.asset.asset')
        res = super(stock_quant, self).move_quants_write(cr, uid, quants, move, location_dest_id,  dest_package_id, context=context)
        #condition checking if product has an asset category and is a delivery to customer it closes the asset
        if move.product_id.valuation == 'real_time' and move.product_id.asset_categ and move.location_dest_id.usage =='customer':
            for each_quant in quants:
                asset_val = asset_obj.search(cr,uid,[('quant','=',each_quant.id)],context=context)
                if asset_val:
                    asset_obj.write(cr,uid,asset_val[0],{'state': 'close'}, context=context)
        return res
    
 
    
    


