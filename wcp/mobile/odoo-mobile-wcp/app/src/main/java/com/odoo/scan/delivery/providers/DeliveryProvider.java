package com.odoo.scan.delivery.providers;

import android.content.Context;
import android.net.Uri;

import com.odoo.orm.OModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.ProductModel;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 28/12/15.
 */
public class DeliveryProvider extends OContentProvider {

    public static String AUTHORITY = "com.odoo.scan.delivery.providers";
    public static final String PATH = "delivery.cylinder";
    public static final Uri CONTENT_URI = OContentProvider.buildURI(AUTHORITY,	PATH);

    @Override
    public OModel model(Context context) {
        return new DeliveryCylinderModel(context);
    }

    @Override
    public String authority() {
        return DeliveryProvider.AUTHORITY;
    }

    @Override
    public String path() {
        return DeliveryProvider.PATH;
    }

    @Override
    public Uri uri() {
        return DeliveryProvider.CONTENT_URI;
    }
}
