package com.odoo.scan.product.tasks;

import android.content.Context;

import com.odoo.App;
import com.odoo.orm.ODataRow;
import com.odoo.orm.OModel;
import com.odoo.orm.OSyncHelper;
import com.odoo.scan.models.ProductModel;
import com.telly.groundy.GroundyTask;
import com.telly.groundy.TaskResult;

import java.util.List;

import odoo.ODomain;

/**
 * Created by bista on 24/8/15.
 */
public class SearchProductBarcode extends GroundyTask{
    @Override
    protected TaskResult doInBackground() {
        try {
            Context mContext = null;
            OModel model = new ProductModel(getContext());
            String mID = getStringArg("serial");
            String where = ProductModel.fields.DEFAULT_CODE + " = ?";
            String[] whereArgs = new String[]{mID};

            ProductModel product = new ProductModel(getContext());

            List<ODataRow> result = product.select(where,whereArgs);

            if (!result.isEmpty()) {
                return succeeded().add("row", result.get(0));
            }
            ODomain domain = new ODomain();
            domain.add(ProductModel.fields.DEFAULT_CODE, "=", mID);

            model.setUser(((App) getContext().getApplicationContext()).getUser());
            OSyncHelper odooSyncHelper = model.getSyncHelper();

            if (odooSyncHelper != null && odooSyncHelper.syncWithServer(domain)) {
                result = model.select(where, whereArgs);
                if (!result.isEmpty()) {
                    return succeeded().add("row", result.get(0));
                };
            }

        }catch (Exception e) {
            e.printStackTrace();

        }
        return failed().add("msg", "No Product available");
    }


}
