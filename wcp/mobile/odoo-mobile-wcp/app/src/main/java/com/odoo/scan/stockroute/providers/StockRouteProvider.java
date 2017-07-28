package com.odoo.scan.stockroute.providers;

import android.content.Context;
import android.net.Uri;

import com.odoo.orm.OModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.StockRouteModel;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 28/12/15.
 */
public class StockRouteProvider extends OContentProvider {

    public static String AUTHORITY = "com.odoo.scan.stockroute.providers";
    public static final String PATH = "stock.route";
    public static final Uri CONTENT_URI = OContentProvider.buildURI(AUTHORITY,	PATH);

    @Override
    public OModel model(Context context) {
        return new StockRouteModel(context);
    }

    @Override
    public String authority() {
        return StockRouteProvider.AUTHORITY;
    }

    @Override
    public String path() {
        return StockRouteProvider.PATH;
    }

    @Override
    public Uri uri() {
        return StockRouteProvider.CONTENT_URI;
    }
}
