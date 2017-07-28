package com.odoo.scan.models;

import android.content.Context;
import com.odoo.base.ir.providers.model.ModelProvider;
import com.odoo.orm.OColumn;
import com.odoo.orm.OModel;
import com.odoo.orm.types.OInteger;
import com.odoo.orm.types.OVarchar;
import com.odoo.support.provider.OContentProvider;

public class ProductModel extends OModel {

    Context mContext = null;
    OColumn name = new OColumn("Name", OVarchar.class);
    OColumn default_code = new OColumn("Internal Reference", OVarchar.class);
    OColumn lst_price = new OColumn("Public price", OInteger.class);
    OColumn qty_available = new OColumn("Quantity", OInteger.class);

    public interface fields {
        String ID = "id";
        String NAME = "name";
        String QUNATITY = "qty_available";
        String LIST_PRICE = "lst_price";
        String DEFAULT_CODE = "default_code";
    }

    public ProductModel(Context context) {
        super(context, "product.product");
        mContext = context;
    }

    @Override
    public String getModelName() {
        return "product.product";
    }

    @Override
    public OContentProvider getContentProvider() {
        return new ModelProvider();
    }
}