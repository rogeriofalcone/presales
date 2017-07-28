package com.odoo.scan.models;

import android.content.Context;

import com.odoo.base.ir.providers.model.ModelProvider;
import com.odoo.base.res.ResPartner;
import com.odoo.orm.OColumn;
import com.odoo.orm.OModel;
import com.odoo.orm.types.OVarchar;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 5/1/16.
 */
public class EmployeeModel extends OModel {

    Context mContext = null;
    OColumn name = new OColumn("Name", OVarchar.class);
    OColumn user_id = new OColumn("User",ResPartner.class, OColumn.RelationType.ManyToOne);


    public EmployeeModel(Context mContext)
         {
        super(mContext, "hr.employee");
    }

    @Override
    public String getModelName() {
        return "hr.employee";
    }

    @Override
    public OContentProvider getContentProvider() {
        return new ModelProvider();
    }

};
