from openerp import models,fields,api


class stock_picking(models.Model):
    _inherit = 'stock.picking'

#    User define function for create invoice line
    @api.v7
    def _generate_order_line_invoice_line(self, cr, uid, order_line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        line_list=[]
        for line in order_line:
            if not line.invoiced:
                if not account_id:
                    if line.product_id:
                        account_id = line.product_id.property_account_income.id
                        if not account_id:
                            account_id = line.product_id.categ_id.property_account_income_categ.id
                        if not account_id:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define income account for this product: "%s" (id:%d).') % \
                                        (line.product_id.name, line.product_id.id,))
                    else:
                        prop = self.pool.get('ir.property').get(cr, uid,
                                'property_account_income_categ', 'product.category',
                                context=context)
                        account_id = prop and prop.id or False
                uosqty = line.product_uom_qty
                uos_id = line.product_uom.id
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
                fpos = line.order_id.fiscal_position or False
                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
                if not account_id:
                    raise osv.except_osv(_('Error!'),
                                _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
                res = {
                    'name': line.name,
                    'sequence': line.sequence,
                    'origin': line.order_id.name,
                    'account_id': account_id,
                    'price_unit': pu,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                }
                line_list.append((0,0,res))
        return line_list

#    User define function for create invoice
    @api.v7
    def generate_create_invoice(self,cr,uid,sale_line,order_id,context=None):

        inv_obj = self.pool.get('account.invoice')
        if sale_line:
            invoice_lines=self._generate_order_line_invoice_line(cr,uid,sale_line,account_id=False,context=context)
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order_id.company_id.id)],
            limit=1)
        invoice_vals = {
            'name': order_id.client_order_ref or '',
            'origin': order_id.name,
            'type': 'out_invoice',
            'reference': order_id.client_order_ref or order_id.name,
            'account_id': order_id.partner_invoice_id.property_account_receivable.id,
            'partner_id': order_id.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': (invoice_lines if invoice_lines else []),
            'currency_id': order_id.pricelist_id.currency_id.id,
            'comment': order_id.note,
            'payment_term': order_id.payment_term and order_id.payment_term.id or False,
            'fiscal_position': order_id.fiscal_position.id or order_id.partner_invoice_id.property_account_position.id,
#            'date_invoice': context.get('date_invoice', False),
            'company_id': order_id.company_id.id,
            'user_id': order_id.user_id and order_id.user_id.id or False,
            'section_id' : order_id.section_id.id
        }
        return inv_obj.create(cr, uid, invoice_vals, context=context)

######    inherit for create invoice from delivery functionality
    @api.v7
    def _invoice_create_line(self, cr, uid, moves, journal_id, inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        invoices = {}
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(cr, uid, moves, inv_type, context=context)
        product_price_unit = {}
        sale_line = list(set([mv.procurement_id.sale_line_id for mv in moves if mv.procurement_id.sale_line_id.product_id.container_ok==True]))
        if sale_line:
            invoice_id=self.generate_create_invoice(cr,uid,sale_line,sale_line[0].order_id)
            key = (sale_line[0].order_id.partner_id.id, sale_line[0].order_id.currency_id.id, sale_line[0].order_id.company_id.id, sale_line[0].order_id.user_id.id)
            invoices[key] = invoice_id
            self.pool.get('sale.order').write(cr, uid, sale_line[0].order_id.id, {
                'invoice_ids': [(4, invoice_id)],
            })
            move_obj.write(cr, uid, [mv.id for mv in moves], {'invoice_state': 'invoiced'}, context=context)
        else:
            for move in moves:
                company = move.company_id
                origin = move.picking_id.name
                partner, user_id, currency_id = move_obj._get_master_data(cr, uid, move, company, context=context)

                key = (partner, currency_id, company.id, user_id)
                invoice_vals = self._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)

                if key not in invoices:
                    # Get account and payment terms
                    invoice_id = self._create_invoice_from_picking(cr, uid, move.picking_id, invoice_vals, context=context)
                    invoices[key] = invoice_id
                else:
                    invoice = invoice_obj.browse(cr, uid, invoices[key], context=context)
                    if not invoice.origin or invoice_vals['origin'] not in invoice.origin.split(', '):
                        invoice_origin = filter(None, [invoice.origin, invoice_vals['origin']])
                        invoice.write({'origin': ', '.join(invoice_origin)})

                invoice_line_vals = move_obj._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
                invoice_line_vals['invoice_id'] = invoices[key]
                invoice_line_vals['origin'] = origin
                if not is_extra_move[move.id]:
                    product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']] = invoice_line_vals['price_unit']
                if is_extra_move[move.id] and (invoice_line_vals['product_id'], invoice_line_vals['uos_id']) in product_price_unit:
                    invoice_line_vals['price_unit'] = product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']]
                if is_extra_move[move.id]:
                    desc = (inv_type in ('out_invoice', 'out_refund') and move.product_id.product_tmpl_id.description_sale) or \
                        (inv_type in ('in_invoice','in_refund') and move.product_id.product_tmpl_id.description_purchase)
                    invoice_line_vals['name'] += ' ' + desc if desc else ''
                    if extra_move_tax[move.picking_id, move.product_id]:
                        invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[move.picking_id, move.product_id]
                    #the default product taxes
                    elif (0, move.product_id) in extra_move_tax:
                        invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[0, move.product_id]

                move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)
                move_obj.write(cr, uid, move.id, {'invoice_state': 'invoiced'}, context=context)

        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoices.values()
