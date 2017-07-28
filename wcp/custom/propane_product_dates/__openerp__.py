# -*- encoding: utf-8 -*-

{
    'name' : 'Propane Product Dates',
    'version' : '0.1',
    'author' : 'Simplify Solutions',
    'category' : 'Specific Industry Applications',
    'website': 'https://www.simplifycloud.com',
    'depends' : ['sale_product_container_rental'],
    'description': """
Track different dates on propane cylinder products
======================================================

Following dates can be tracked:
-------------------------------
    - recertification frequency
    - last / next date recertified
    - 5 year relief valve inspection
    - manufacture date

Also implements the removal strategy First Expiry First Out (FEFO) widely used, for example, in food industries.
""",
    'data' : [
        'views/product_view.xml',
        'product_expiry_data.xml',
        ],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

