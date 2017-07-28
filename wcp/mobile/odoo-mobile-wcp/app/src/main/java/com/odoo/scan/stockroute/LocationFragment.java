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

import com.odoo.base.res.ResPartner;
import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
import com.odoo.scan.models.AnalyticDeliveryModel;
import com.odoo.scan.models.StockRouteModel;
import com.odoo.support.AppScope;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.drawer.DrawerItem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Created by bista on 28/12/15.
 */
public class LocationFragment extends BaseFragment implements IProcessData {

    public static final String TAG = LocationFragment.class.getSimpleName();

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
        return new AnalyticDeliveryModel(context);
    }

    @Override
    public void onSkidClicked(String product) {

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
            TextView c = (TextView) arg1.findViewById(R.id.location_id);
            String location_id = c.getText().toString();
            String strtext = getArguments().getString("stock_route_id");
            Bundle args = new Bundle();
            args.putString("location_id", location_id);
            args.putString("stock_route_id", strtext);
            DeliveryFragment fragment2 = new DeliveryFragment();
            FragmentManager fragmentManager = getActivity().getSupportFragmentManager();
            FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
            fragment2.setArguments(args);
            fragmentTransaction.replace(R.id.fragment_container, fragment2);
            fragmentTransaction.addToBackStack(null);
            fragmentTransaction.commit();
        }
    };

    class SingleRow {
        String name;
        Integer id;

        SingleRow(String name, Integer id)
        {
            this.name=name;
            this.id = id;
        }
    }

    class VcAdapter extends BaseAdapter
    {
        ArrayList<SingleRow> list;
        Context context;
        VcAdapter(Context c) {
            context = c;
            list = new ArrayList<SingleRow>();
            Map dictionary = new HashMap();

            Set<SingleRow> uniqueValues = new HashSet<SingleRow>();
            scope = new AppScope(getActivity());
            String strtext = getArguments().getString("stock_route_id");
            Integer mID = scope.User().getUser_id();
            String where = AnalyticDeliveryModel.fields.STOCK_ROUTE_ID + " = ? ORDER BY sequence ";
            String[] whereArgs = new String[]{strtext};
            List<ODataRow> resultProduct = new AnalyticDeliveryModel(getActivity()).select(where,whereArgs);

            for (ODataRow i : resultProduct) {
                String location_name = i.getM2ORecord(AnalyticDeliveryModel.fields.LOCATION_ID).browse().get("name").toString();
                Integer location_id = i.getM2ORecord(AnalyticDeliveryModel.fields.LOCATION_ID).browse().getInt("_id");
                Integer seq = i.getInt("sequence");

                if(dictionary.containsKey(location_id)) {

                }else {
                    dictionary.put(location_id, location_name);
                    list.add(new SingleRow(location_name, location_id));

                }
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
            View row = inflater.inflate(R.layout.item_stocklocation, viewGroup, false);

            TextView name = (TextView) row.findViewById(R.id.location_name);
            TextView stock_route_id = (TextView) row.findViewById(R.id.location_id);

            SingleRow temp=list.get(i);
            String strI = String.valueOf(temp.id);
            name.setText(temp.name);
            stock_route_id.setText(strI);
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


}
