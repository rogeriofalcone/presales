package com.odoo.scan.stockroute.tasks;

import com.odoo.App;
import com.odoo.orm.ODataRow;
import com.odoo.orm.OModel;
import com.odoo.orm.OSyncHelper;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.telly.groundy.GroundyTask;
import com.telly.groundy.TaskResult;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.Serializable;
import java.util.HashMap;
import java.util.List;

import odoo.OArguments;
import odoo.ODomain;

/**
 * Created by bista on 29/12/15.
 */
public class DeliveryTask extends GroundyTask {
    public static final String TAG = DeliveryTask.class.getSimpleName();
    private DeliveryCylinderModel doModel;
    private HashMap<String, ODomain> mDomain = new HashMap<>();

    @Override
    protected TaskResult doInBackground() {
        ODataRow doInProgress = null;
        Boolean result1 = false;
        OModel model = new DeliveryCylinderModel(getContext());

        String mID = getStringArg("delivery_id");
        String actual_in = getStringArg("actual_in");
        String actual_out = getStringArg("actual_out");

        model.setUser(((App) getContext().getApplicationContext()).getUser());
        OSyncHelper odooSyncHelper = model.getSyncHelper();

        JSONObject context = new JSONObject();
        JSONArray ids = new JSONArray();
        JSONObject args22 = new JSONObject();

        ids.put(Integer.parseInt(mID));
        try {
            args22.put("actual_in",Integer.parseInt(actual_in));
            args22.put("actual_out",Integer.parseInt(actual_out));
            args22.put("state","open");

        } catch (JSONException e) {
            e.printStackTrace();
        }

        OArguments args = new OArguments();

        args.add(ids);
        args.add(args22);
        result1 = (Boolean) odooSyncHelper.callMethod("delivery.cylinder", "write", args, context, null);
        if (!result1) {
            return failed();
        } else {
            return succeeded();
        }
    }
}