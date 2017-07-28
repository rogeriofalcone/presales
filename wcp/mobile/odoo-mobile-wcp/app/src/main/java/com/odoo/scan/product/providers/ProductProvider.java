package com.odoo.scan.product.providers;

import android.content.Context;
import android.net.Uri;
import com.odoo.orm.OModel;
import com.odoo.scan.models.ProductModel;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 25/8/15.
 */
public class ProductProvider extends OContentProvider {

    public static String AUTHORITY = "com.odoo.scan.product.providers";
    public static final String PATH = "product_product";
    public static final Uri CONTENT_URI = OContentProvider.buildURI(AUTHORITY,	PATH);

    @Override
    public OModel model(Context context) {
        return new ProductModel(context);
    }

    @Override
    public String authority() {
        return ProductProvider.AUTHORITY;
    }

    @Override
    public String path() {
        return ProductProvider.PATH;
    }

    @Override
    public Uri uri() {
        return ProductProvider.CONTENT_URI;
    }
}
