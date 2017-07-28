package com.odoo.scan.models;

import android.content.Context;

import com.odoo.base.ir.providers.model.ModelProvider;
import com.odoo.base.res.ResPartner;
import com.odoo.orm.OColumn;
import com.odoo.orm.OModel;
import com.odoo.orm.types.OInteger;
import com.odoo.orm.types.OVarchar;
import com.odoo.support.provider.OContentProvider;

/**
 * Created by bista on 28/12/15.
 */
public class AnalyticDeliveryModel  extends OModel {

    Context mContext = null;

    OColumn name = new OColumn(fields.NAME, OVarchar.class);
    OColumn numbercall = new OColumn(fields.NUMBERCALL, OInteger.class);
    OColumn location_id = new OColumn(fields.LOCATION_ID, ResPartner.class,OColumn.RelationType.ManyToOne);
    OColumn stock_route_id = new OColumn(fields.STOCK_ROUTE_ID, StockRouteModel.class, OColumn.RelationType.ManyToOne);
    OColumn sequence = new OColumn(fields.SEQUENCE,OInteger.class);


    public interface fields {
        String ID = "id";
        String LOCATION_ID = "location_id";
        String NUMBERCALL = "numbercall";
        String STOCK_ROUTE_ID = "stock_route_id";
        String NAME= "name";
        String SEQUENCE = "sequence";

    }


    public AnalyticDeliveryModel(Context mContext) {
        super(mContext, "account.analytic.delivery");
    }

    @Override
    public String getModelName() {
        return "account.analytic.delivery";
    }

    @Override
    public OContentProvider getContentProvider() {
        return new ModelProvider();
    }
}
