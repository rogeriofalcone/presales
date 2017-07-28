package com.odoo.scan.stockroute;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
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

import com.odoo.MainActivity;
import com.odoo.base.res.ResPartner;
import com.odoo.base.res.ResUsers;
import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
import com.odoo.scan.models.AnalyticDeliveryModel;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.EmployeeModel;
import com.odoo.scan.models.ProductModel;
import com.odoo.scan.models.StockRouteModel;
import com.odoo.support.AppScope;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.drawer.DrawerItem;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Created by bista on 28/12/15.
 */
public class StockRouteFragment extends BaseFragment implements IProcessData {

    public static final String TAG = StockRouteFragment.class.getSimpleName();

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
        return new StockRouteModel(context);
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

//        listview.setBackgroundColor(Color.BLUE);
        actionbar().setTitle(_s(R.string.title_configuration));

        return rootView;
    }

    private AdapterView.OnItemClickListener onItemClickListener = new AdapterView.OnItemClickListener() {

        @Override
        public void onItemClick(AdapterView<?> arg0, View arg1, int position,
                                long arg3) {
            // TODO Auto-generated method stub
            Object item=arg0.getItemAtPosition(position);
            String value = item.toString();
            TextView c = (TextView) arg1.findViewById(R.id.stock_route_id);
            String stock_route_id = c.getText().toString();
            Bundle args = new Bundle();
            args.putString("stock_route_id", stock_route_id);
            LocationFragment fragment2 = new LocationFragment();
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
        String date_next;
        Integer contact_per_id;

        SingleRow(String name, Integer id, String date_next, Integer contact_per_id)
        {
            this.name=name;
            this.id = id;
            this.date_next = date_next;
            this.contact_per_id = contact_per_id;
        }
    }

    class VcAdapter extends BaseAdapter
    {
        ArrayList<SingleRow> list;
        ArrayList<SingleRow> list1;
        Context context;
        VcAdapter(Context c) {
            context = c;
            list = new ArrayList<SingleRow>();
            list1 = new ArrayList<SingleRow>();
            ArrayList<Integer> emp_list = new ArrayList<Integer>();

            ArrayList<SingleRow> final_list = new ArrayList<SingleRow>();
            scope = new AppScope(getActivity());

            Integer mID = scope.User().getUser_id();
            String where12 = "SELECT * FROM stock_route ORDER BY DATE_NEXT ASC ";
            List<ODataRow> resultProduct112 = new StockRouteModel(getActivity()).query(where12, null);
//            String emp_id = "SELECT * hr.employee WHERE id='1'";

//            String where123 = "SELECT * FROM res_users WHERE _id='1'";
//            String where = ResUsers.fields.STOCK_ROUTE_ID + " = ? ";
//            String[] whereArgs = new String[]{strtext};

            List<ODataRow> resultemployee = new EmployeeModel(getActivity()).select(null, null);

//            System.out.println("tsest >>>>>>>>>>>>>."+resultProduct112);

            for (ODataRow i : resultemployee) {
                if (mID == i.getM2ORecord("user_id").browse().getInt("id")){
//                    System.out.println("TEST RECORDS >>>>>>>>>>>>>>>>>>"+i.getM2ORecord("user_id").browse().getInt("id") + mID + i.getInt("id"));
                    emp_list.add(i.getInt("_id"));

                }
//                List<ODataRow> resultProduct = new AnalyticDeliveryModel(getActivity()).select(where,whereArgs);


            }

            SimpleDateFormat dateFormat= new SimpleDateFormat("yyyy-MM-dd", Locale.ENGLISH);
            String cDateTime=dateFormat.format(new Date());


            for (ODataRow i : resultProduct112) {
                if (emp_list.contains(i.getInt("contact_per_id"))) {
                    System.out.println("test values >>>>>>>>>>>>>>>>>."+ i);
                    if (i.getString(StockRouteModel.fields.DATE_NEXT).equals(cDateTime)) {

                        list1.add(new SingleRow(i.getString(StockRouteModel.fields.NAME), i.getInt("_id"), i.getString(StockRouteModel.fields.DATE_NEXT), i.getInt(StockRouteModel.fields.CONTACT_PER_ID)));

                    } else {
                        list.add(new SingleRow(i.getString(StockRouteModel.fields.NAME), i.getInt("_id"), i.getString(StockRouteModel.fields.DATE_NEXT), i.getInt(StockRouteModel.fields.CONTACT_PER_ID)));
                    }
                }
            }
            list1.addAll(list);
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
            View row = inflater.inflate(R.layout.item_stockmove, viewGroup, false);

            TextView name = (TextView) row.findViewById(R.id.stock_route_name);
            TextView stock_route_id = (TextView) row.findViewById(R.id.stock_route_id);
            TextView date_next = (TextView)row.findViewById(R.id.date_next);

            SingleRow temp=list1.get(i);
            String strI = String.valueOf(temp.id);
            name.setText(temp.name);
            stock_route_id.setText(strI);
            date_next.setText(temp.date_next);
            return row;
        }

    }
    @Override
    public void onResume() {
        super.onResume();
        actionbar().show();
        actionbar().setTitle(_s(R.string.stock_route_title));
    }

    @Override
    public List<DrawerItem> drawerMenus(Context context) {
        return null;
    }

    @Override
    public void onSkidClicked(String product) {
        Log.i(TAG, "");
    }


}
