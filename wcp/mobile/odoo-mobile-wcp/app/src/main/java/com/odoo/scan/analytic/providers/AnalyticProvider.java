package com.odoo.scan.analytic.providers;

import android.content.Context;
import android.net.Uri;

import com.odoo.orm.OModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 4/1/16.
 */
public class AnalyticProvider  extends OContentProvider {

        public static String AUTHORITY = "com.odoo.scan.analytic.providers";
        public static final String PATH = "account.analytic.delivery";
        public static final Uri CONTENT_URI = OContentProvider.buildURI(AUTHORITY,	PATH);

        @Override
        public OModel model(Context context) {
            return new DeliveryCylinderModel(context);
        }

        @Override
        public String authority() {
            return AnalyticProvider.AUTHORITY;
        }

        @Override
        public String path() {
            return com.odoo.scan.analytic.providers.AnalyticProvider.PATH;
        }

        @Override
        public Uri uri() {
            return com.odoo.scan.analytic.providers.AnalyticProvider.CONTENT_URI;
        }
}
