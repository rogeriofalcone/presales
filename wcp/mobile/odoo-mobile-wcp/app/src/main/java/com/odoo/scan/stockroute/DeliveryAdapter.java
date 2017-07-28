package com.odoo.scan.stockroute;

import android.content.Context;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.odoo.crm.R;
import com.odoo.scan.PlannedMove;

import java.util.ArrayList;
import java.util.HashMap;

/**
 * Created by bista on 29/12/15.
 */
public class DeliveryAdapter extends RecyclerView.Adapter <RecyclerView.ViewHolder> {

    private final static String TAG = DeliveryAdapter.class.getSimpleName();
    private Context mContext = null;
    private ArrayList<String> mKeys;
    private HashMap<String, PlannedMove> plannedMoveHash;

    public DeliveryAdapter(Context context, ProductViewHolder.ISkidClick listener) {
        ProductViewHolder.ISkidClick mListener = listener;
        mContext = context;
        plannedMoveHash = new HashMap<String, PlannedMove>();
        mKeys = new ArrayList<String>();
    }

    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_product_detail, parent, false);
        return new ProductViewHolder(v);
    }

    @Override
    public void onBindViewHolder(RecyclerView.ViewHolder holder, int position) {
        PlannedMove plannedMove = plannedMoveHash.get(mKeys.get(position));
        ((ProductViewHolder) holder).quantity.setText("12");
    }

    @Override
    public int getItemCount() {
        return 0;
    }

    public static class ProductViewHolder extends RecyclerView.ViewHolder {

        public TextView name;
        public TextView quantity;

        public ProductViewHolder(View v) {
            super(v);
            name = (TextView) v.findViewById(R.id.product_name);
            quantity = (TextView) v.findViewById(R.id.quantity);
        }

        public static interface ISkidClick {
            public void onSkidClicked(String product);
        }
    }
}
