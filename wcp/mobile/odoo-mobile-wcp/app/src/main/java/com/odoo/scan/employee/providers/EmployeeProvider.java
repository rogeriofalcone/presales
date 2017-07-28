package com.odoo.scan.employee.providers;

import android.content.Context;
import android.net.Uri;

import com.odoo.orm.OModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 5/1/16.
 */
public class EmployeeProvider extends OContentProvider {

    public static String AUTHORITY = "com.odoo.scan.employee.providers";
    public static final String PATH = "hr.employee";
    public static final Uri CONTENT_URI = OContentProvider.buildURI(AUTHORITY,	PATH);

    @Override
    public OModel model(Context context) {
        return new DeliveryCylinderModel(context);
    }

    @Override
    public String authority() {
        return EmployeeProvider.AUTHORITY;
    }

    @Override
    public String path() {
        return EmployeeProvider.PATH;
    }

    @Override
    public Uri uri() {
        return EmployeeProvider.CONTENT_URI;
    }
}
