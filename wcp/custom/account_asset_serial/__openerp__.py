{
    'name': 'Account Asset Serial',
    'version': '1.1',
    'category': 'Asset',
    'description': """
        Account Asset Serial
    """,
    'author': 'Bista Solutions Pvt Ltd',
    'website': 'www.bistasolutions.com',
    'depends': ['account_asset_management', 'stock_account','stock', 'product'],
    'data': [
            'views/product_view.xml',
            'views/account_asset_view.xml',
            'views/data.xml',
    ],
    'installable': True,
    'auto_install': False,
}