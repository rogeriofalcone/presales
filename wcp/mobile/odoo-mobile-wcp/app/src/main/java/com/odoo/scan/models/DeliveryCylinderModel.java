package com.odoo.scan.models;

import android.content.Context;

import com.odoo.base.ir.providers.model.ModelProvider;
import com.odoo.base.res.ResPartner;
import com.odoo.orm.OColumn;
import com.odoo.orm.OModel;
import com.odoo.orm.types.OInteger;
import com.odoo.orm.types.OText;
import com.odoo.support.provider.OContentProvider;
import com.odoo.util.ODate;

/**
 * Created by bista on 10/12/15.
 */
public class DeliveryCylinderModel extends OModel {

    Context mContext = null;

    OColumn partner_id = new OColumn(fields.PARTNER_ID, ResPartner.class, OColumn.RelationType.ManyToOne);
    OColumn product_id = new OColumn(fields.PRODUCT_ID, ProductModel.class, OColumn.RelationType.ManyToOne);
    OColumn schedule_in = new OColumn(fields.SCHEDULE_IN, OInteger.class);
    OColumn schedule_out = new OColumn(fields.SCHEDULE_OUT, OInteger.class);
    OColumn actual_in = new OColumn(fields.ACTUAL_IN, OInteger.class);
    OColumn actual_out = new OColumn(fields.ACTUAL_OUT, OInteger.class);
    OColumn stock_route_id = new OColumn(fields.STOCK_ROUTE_ID, StockRouteModel.class, OColumn.RelationType.ManyToOne);
    OColumn state = new OColumn(fields.STATE, OText.class);
    OColumn sequence = new OColumn(fields.SEQUENCE,OInteger.class);


    public interface fields {
        String ID = "id";
        String STATE = "state";
        String SCHEDULE_OUT = "schedule_out";
        String SCHEDULE_IN = "schedule_in";
        String PRODUCT_ID = "product_id";
        String PARTNER_ID = "partner_id";
//        String DELIVERY_DATE = "delivery_date";
        String ACTUAL_IN = "actual_in";
        String ACTUAL_OUT = "actual_out";
        String STOCK_ROUTE_ID = "stock_route_id";
        String SEQUENCE = "sequence";
    }


    public DeliveryCylinderModel(Context mContext) {
        super(mContext, "delivery.cylinder");
    }

    @Override
    public String getModelName() {
        return "delivery.cylinder";
    }

    @Override
    public OContentProvider getContentProvider() {
        return new ModelProvider();
    }
}
