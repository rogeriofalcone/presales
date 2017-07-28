package com.odoo.scan.models;

import android.content.Context;

import com.odoo.base.ir.providers.model.ModelProvider;
import com.odoo.base.res.ResPartner;
import com.odoo.orm.OColumn;
import com.odoo.orm.OModel;
import com.odoo.orm.types.ODateTime;
import com.odoo.orm.types.OInteger;
import com.odoo.orm.types.OText;
import com.odoo.orm.types.OVarchar;
import com.odoo.support.provider.OContentProvider;
import com.odoo.orm.types.ODate;

/**
 * Created by bista on 14/12/15.
 */
public class StockRouteModel extends OModel  {

    Context mContext = null;

    OColumn name = new OColumn(fields.NAME, OText.class);
    OColumn delivery_lines = new OColumn(fields.DELIVERY_LINE, AnalyticDeliveryModel.class, OColumn.RelationType.OneToMany);
    OColumn id = new OColumn(fields.ID, OInteger.class);
    OColumn date_next = new OColumn(fields.DATE_NEXT, ODateTime.class);
    OColumn contact_per_id = new OColumn(fields.CONTACT_PER_ID, EmployeeModel.class, OColumn.RelationType.ManyToOne);
//    OColumn sequence = new OColumn(fields.SEQUENCE,OInteger.class);

    public interface fields {
        String ID = "id";
        String NAME = "name";
        String DELIVERY_LINE = "delivery_lines";
        String DATE_NEXT = "date_next";
        String CONTACT_PER_ID = "contact_per_id";
//        String SEQUENCE = "sequence";
    }

    public StockRouteModel(Context mContext) {
        super(mContext, "stock.route");
    }

    @Override
    public String getModelName() {
        return "stock.route";
    }

    @Override
    public OContentProvider getContentProvider() {
        return new ModelProvider();
    }

}
