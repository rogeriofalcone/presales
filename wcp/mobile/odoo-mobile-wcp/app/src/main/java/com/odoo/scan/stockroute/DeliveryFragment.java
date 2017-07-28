package com.odoo.scan.stockroute;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
import com.odoo.scan.models.AnalyticDeliveryModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.StockRouteModel;
import com.odoo.support.AppScope;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.StringUtils;
import com.odoo.util.drawer.DrawerItem;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by bista on 28/12/15.
 */
public class DeliveryFragment extends BaseFragment implements IProcessData {

    public static final String TAG = DeliveryFragment.class.getSimpleName();

    public IOperationFlow mCallbacks = sDummyCallbacks;

    private static IOperationFlow sDummyCallbacks = new IOperationFlow() {


        @Override
        public void onValidFirstStep(Bundle args) {

        }

        @Override
        public void onOperationCancelled() {

        }

        @Override
        public void onStockMoveApproved(int id) {

        }

        @Override
        public void onDOApproved() {

        }
    };

    @Override
    public void processData(String line) {

    }

    @Override
    public void populateScreen(Bundle args) {

    }


    @Override
    public void onAttach(Activity activity) {
        super.onAttach(activity);
        try {
            mCallbacks = (IOperationFlow) getParentFragment();
        } catch (ClassCastException e) {
            throw new ClassCastException("Parent must implement " + TAG + ".Callbacks");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mCallbacks = sDummyCallbacks;
    }

    @Override
    public Object databaseHelper(Context context) {
        return new DeliveryCylinderModel(context);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_stockmove, container, false);
        ListView listview =(ListView)rootView.findViewById(R.id.listview);
        VcAdapter adapter = new VcAdapter(getActivity());
        listview.setAdapter(adapter);
        listview.setOnItemClickListener(onItemClickListener);

        return rootView;
    }

    private AdapterView.OnItemClickListener onItemClickListener = new AdapterView.OnItemClickListener() {

        @Override
        public void onItemClick(AdapterView<?> arg0, View arg1, int position,
                                long arg3) {
            // TODO Auto-generated method stub
            Object item=arg0.getItemAtPosition(position);
            String value = item.toString();
            TextView c = (TextView) arg1.findViewById(R.id.delivery_id);
            TextView partner_name = (TextView)arg1.findViewById(R.id.delivery_partner_name);
            TextView product_name = (TextView)arg1.findViewById(R.id.delivery_product_id);
            TextView actual_in = (TextView)arg1.findViewById(R.id.delivery_in);
            TextView actual_out = (TextView)arg1.findViewById(R.id.delivery_out);

            String delivery_id = c.getText().toString();
            String partner_name_string = partner_name.getText().toString();
            String product_name_string = product_name.getText().toString();
            String actual_in_string = actual_in.getText().toString();
            String actual_out_string = actual_out.getText().toString();

            Bundle args = new Bundle();
            args.putString("delivery_id", delivery_id);
            args.putString("partner_name", partner_name_string);
            args.putString("product_name", product_name_string);
            args.putString("actual_in",actual_in_string);
            args.putString("actual_out",actual_out_string);


            FragmentManager fm = getFragmentManager();
            DeliveryDetailFragment dialogFragment = new DeliveryDetailFragment ();
            dialogFragment.setArguments(args);
            dialogFragment.show(fm, "Delivery Fragment");
        }
    };

    class SingleRow {
        String partner_name;
        String product_name;
        String actual_in;
        String actual_out;
        String delivery_id;
        String state;
        Integer sequence;

        SingleRow(String partner_name,
                String product_name,
                  String actual_in,
                  String actual_out,
                  String delivery_id, String state, Integer sequence)
        {
            this.partner_name=partner_name;
            this.actual_in = actual_in;
            this.state = state;
            this.actual_out = actual_out;
            this.product_name = product_name;
            this.delivery_id = delivery_id;
            this.sequence = sequence;
        }
    }

    class VcAdapter extends BaseAdapter
    {
        ArrayList<SingleRow> list;
        Context context;
        VcAdapter(Context c) {
            context = c;
            list = new ArrayList<SingleRow>();
            scope = new AppScope(getActivity());
            String strtext = getArguments().getString("location_id");
            String stock_route_id = getArguments().getString("stock_route_id");
            Integer mID = scope.User().getUser_id();

            String where = DeliveryCylinderModel.fields.PARTNER_ID + " = ? ORDER BY sequence AND " + DeliveryCylinderModel.fields.STOCK_ROUTE_ID + " = ?";
            String[] whereArgs = new String[]{strtext,stock_route_id};
            List<ODataRow> resultProduct = new DeliveryCylinderModel(getActivity()).select(where,whereArgs);

            for (ODataRow i : resultProduct) {
                String partner_name = i.getM2ORecord(DeliveryCylinderModel.fields.PARTNER_ID).browse().get("name").toString();
                String product_name = i.getM2ORecord(DeliveryCylinderModel.fields.PRODUCT_ID).browse().get("name").toString();
                String actual_in = i.getString(DeliveryCylinderModel.fields.ACTUAL_IN);
                String actual_out = i.getString(DeliveryCylinderModel.fields.ACTUAL_OUT);
                String delivery_id = i.getString(DeliveryCylinderModel.fields.ID);
                String state = i.getString(DeliveryCylinderModel.fields.STATE);
                Integer sequence = i.getInt(DeliveryCylinderModel.fields.SEQUENCE);

                list.add(new SingleRow(partner_name,product_name,actual_in,actual_out,delivery_id,state,sequence));
            }
        }

        @Override
        public int getCount() {
            // TODO Auto-generated method stub
            return list.size();
        }

        @Override
        public Object getItem(int i) {
            // TODO Auto-generated method stub
            return list.get(i);
        }

        @Override
        public long getItemId(int i) {
            // TODO Auto-generated method stub
            return 0;
        }

        @Override
        public View getView(int i, View view, ViewGroup viewGroup) {
            // TODO Auto-generated method stub
            LayoutInflater inflater=(LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            View row = inflater.inflate(R.layout.item_delivery, viewGroup, false);

            TextView partner_name = (TextView) row.findViewById(R.id.delivery_partner_name);
            TextView delivery_id = (TextView) row.findViewById(R.id.delivery_id);
            TextView actual_out = (TextView) row.findViewById(R.id.delivery_out);
            TextView actual_in = (TextView) row.findViewById(R.id.delivery_in);
            TextView product_name = (TextView) row.findViewById(R.id.delivery_product_id);

            SingleRow temp=list.get(i);
            partner_name.setText(temp.partner_name);
            delivery_id.setText(temp.delivery_id);
            actual_out.setText(temp.actual_out);
            actual_in.setText(temp.actual_in);
            product_name.setText(temp.product_name);

            System.out.println("vals >>>>>>>>."+temp.state);
            if (temp.state.toString().contains("done")){

                row.setBackgroundColor(R.color.gray_light);
            }


            return row;
        }

    }
    @Override
    public void onResume() {

        super.onResume();
    }

    @Override
    public List<DrawerItem> drawerMenus(Context context) {
        return null;
    }

    @Override
    public void onSkidClicked(String product) {
        Log.i(TAG, "Skid clicked");
    }

}
