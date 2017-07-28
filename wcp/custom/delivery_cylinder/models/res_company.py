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
from openerp import SUPERUSER_ID
from openerp.osv import orm


class res_company(models.Model):
    _inherit="res.company"
    
    conditions=fields.Text("Conditions")
    conditions_sales_clauses=fields.Text("Conditional Sales Contract Clauses")
    
    
    
res_company()


class account_analytic_account(models.Model):
    _inherit="account.analytic.account"
    
    
    conditions=fields.Text("Conditions")
    
account_analytic_account()