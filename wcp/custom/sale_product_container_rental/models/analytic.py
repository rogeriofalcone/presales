# -*- encoding: utf-8 -*-

# from openerp.osv import osv
from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_analytic_delivery(models.Model):
    _name = 'account.analytic.delivery'
    _description = 'Contract Deliveries'
    _order = 'location_id, sequence'

    name = fields.Char('Name')
    location_id = fields.Many2one('res.partner', string='Location')
    interval_number = fields.Integer('Interval')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    nextcall = fields.Datetime('Next Delivery')
    numbercall = fields.Integer('Number of Deliveries', default=-1,
            help="Number of Deliveries at location. Set to -1 for no limit")
    account_id = fields.Many2one('account.analytic.account', string='Contract',
            ondelete='cascade')
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)

class account_analytic_product_rental(models.Model):
    _name = "account.analytic.product.rental"
    _description = "Rental Units on Contract"

    @api.one
    @api.depends('sale_line_id', 'sale_line_id.procurement_ids')
    def _compute_procurement_and_move(self):
        procurement = False
        in_move = False
        out_move = False
        state = 'cylinder'
        if (
                self.sale_line_id and
                self.sale_line_id.procurement_ids):

            procurement = self.sale_line_id.procurement_ids[0]
            if procurement.move_ids:
                for move in procurement.move_ids:
                    if move.move_dest_id:
                        out_move = move
                    else:
                        in_move = move
            state = 'ordered'
            if out_move and in_move:
                if out_move.state == 'done':
                    state = 'out'
                if out_move.state == 'done' and in_move.state == 'done':
                    state = 'in'
        self.procurement_id = procurement
        self.in_move_id = in_move
        self.out_move_id = out_move
        self.state = state

    product_id = fields.Many2one('product.product', string='Product',
            required=True)
    location_id = fields.Many2one('res.partner', string='Location')
    analytic_account_id = fields.Many2one('account.analytic.account',
            string='Analytic Account')
    name = fields.Char('Description', required=True)
    price_unit = fields.Float('Unit Price', required=True)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    interval_number = fields.Integer('Interval', default=1)
    interval_type = fields.Selection([
        ('month','Months'),
        ('year','Years')],
        'Interval Type', required=True, default='month')
    nextcall = fields.Date('Next Invoice')
    waiver_opt_out = fields.Boolean('Waiver Opt-out')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    sale_id = fields.Many2one('sale.order', string='Sale Order',
            related='sale_line_id.order_id',store=True)
    lot_id = fields.Many2one('stock.production.lot', 'Inventoried Lot/Serial Number')
    procurement_id = fields.Many2one(
        'procurement.order', string="Procurement", readonly=True,
        compute='_compute_procurement_and_move')
    out_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Outgoing Stock Move', readonly=True)
    in_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Return Stock Move', readonly=True)
    state = fields.Selection([
        ('ordered', 'Ordered'),
        ('cylinder', 'Cylinder'),
        ('out', 'Out'),
        ('in', 'Back In'),
        ], string='State', compute='_compute_procurement_and_move',
        readonly=True)

    @api.model
    def create(self, vals):
        aa_id = self.env['account.analytic.account'].browse(vals.get('analytic_account_id'))
        if vals.get('interval_type') == 'month':
            delta = relativedelta(months=vals.get('interval_number', 1))
        else:
            delta = relativedelta(months=vals.get('interval_number', 1))
        lastcall = datetime.now()
        nextcall = lastcall + delta
        if aa_id.rental_lastcall:
            lastcall = datetime.strptime(aa_id.rental_lastcall,
                    DEFAULT_SERVER_DATE_FORMAT)
            nextcall = lastcall + delta
        else:
            aa_id.rental_nextcall = nextcall
        vals.update(nextcall=nextcall)
        return super(account_analytic_product_rental, self).create(vals)

    @api.v7
    def product_id_change(self, cr, uid, ids, product, name='', partner_id=False, price_unit=False, pricelist_id=False, company_id=None, context=None):
        context = context or {}
        ctx = dict(context)
        company_id = company_id or False
        ctx.update({'company_id': company_id, 'force_company': company_id, 'pricelist_id': pricelist_id})

        if not product:
            return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
        if partner_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=ctx)
            if part.lang:
                ctx.update({'lang': part.lang})

        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=ctx)
        result.update({'name':res.partner_ref or False, 'price_unit': res.rental_price or res.list_price or 0.0})
        if res.description:
            result['name'] += '\n'+res.description

        res_final = {'value':result}
        return res_final

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    def _analysis_delivery(self):
        self.delivery_quantity = len(self.child_ids)

    def _remaining_delivery_calc(self):
        if self.delivery_number < 0:
            self.remaining_delivery = -1
        elif self.delivery_number > 0:
            self.remaining_delivery = self.delivery_number - self.delivery_quantity
        else:
            self.remaining_delivery = 0.0

    delivery_quantity = fields.Integer(compute='_analysis_delivery',
            string='Total Deliveries',
            help='The total number of Deliveries for this account')
    delivery_number = fields.Integer('Number of Deliveries',
            default=-1, help="Maximum number of Deliveries. Set to -1 for no limit")
    delivery_offset = fields.Integer('Schedule Days Prior', default=10,
            help="The scheduling offset for Deliveries. For example, '10' will create a Delivery 10 days prior to it's scheduled date")
    remaining_delivery = fields.Integer(compute='_remaining_delivery_calc',
            string='Remaining Deliveries',
            help="Computed using the formula: Number of Deliveries - Total Deliveries")
    use_delivery = fields.Boolean('Use Deliveries')
    delivery_ids = fields.One2many('account.analytic.delivery', 'account_id',
            string='Deliveries')
    contract_type = fields.Selection([
        ('prepaid','Prepaid'), ('on_delivery','On Delivery')],
        default='on_delivery', string='Invoicing')
    rental_product_id = fields.Many2one('product.product', string='Product')
    rental_product_line_ids = fields.One2many('account.analytic.product.rental',
            'analytic_account_id', string='Rental Product Lines')
    rental_description = fields.Text('Description')
    rental_nextcall = fields.Date('Next Rental Invoice')
    rental_lastcall = fields.Date('Last Rental Invoice')
    client_order_ref = fields.Char('Customer Ref.')
    notes = fields.Text('Notes')

    @api.model
    def create(self, vals):
        #TODO: Use default values
        if vals.get('use_delivery',False):
            parent_ids = self.search([('code','=','RNT')])
            vals.update(parent_ids=parent_ids and parent_ids[0] or False)
        if not vals.get('rental_lastcall'):
            vals.update(
                    rental_lastcall = datetime.today() - relativedelta(days=1),
                    )
        return super(account_analytic_account, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
