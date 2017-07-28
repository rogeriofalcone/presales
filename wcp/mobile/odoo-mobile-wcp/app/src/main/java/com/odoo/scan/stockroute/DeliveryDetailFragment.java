package com.odoo.scan.stockroute;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v4.app.DialogFragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.support.v7.widget.GridLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.NumberPicker;
import android.widget.TextView;

import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.ProductModel;
import com.odoo.scan.product.ProductAdapter;
import com.odoo.scan.stockroute.tasks.DeliveryTask;
import com.odoo.support.AppScope;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.ToastFactory;
import com.odoo.util.drawer.DrawerItem;
import com.telly.groundy.Groundy;
import com.telly.groundy.annotations.OnSuccess;
import com.telly.groundy.annotations.Param;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class DeliveryDetailFragment extends DialogFragment implements IProcessData{
    public IOperationFlow mCallbacks = sDummyCallbacks;
    private Integer actual_in_update;
    private Integer actual_out_update;

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
        Groundy.create(DeliveryTask.class)
                .callback(this)
                .arg("delivery_id", line)
                .arg("actual_in",actual_in_update)
                .arg("actual_out",actual_out_update)
                .queueUsing(getActivity().getApplicationContext());
    }



    @Override
    public void populateScreen(Bundle args) {

    }

    @Override
    public Object databaseHelper(Context context) {
        return null;
    }

    @Override
    public void onSkidClicked(String product) {

    }
    @OnSuccess(DeliveryTask.class)
    public void onDOProcessed() {
        dismiss();
        mCallbacks.onDOApproved();

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_delivery, container, false);
        getDialog().setTitle("Update Delivery Detail");
        final String strtext = getArguments().getString("delivery_id");
        String product_name = getArguments().getString("product_name");
        String parent_name= getArguments().getString("partner_name");


        final String actual_in = getArguments().getString("actual_in");
        final String actual_out = getArguments().getString("actual_out");

        View tv = rootView.findViewById(R.id.product_name);
        ((TextView)tv).setText(product_name);
        View tv1 = rootView.findViewById(R.id.partner_name);
        ((TextView)tv1).setText(parent_name);
        View in = rootView.findViewById(R.id.actual_in);
        ((NumberPicker)in).setValue(Integer.parseInt(actual_in));
        View out = rootView.findViewById(R.id.actual_out);
        ((NumberPicker)out).setValue(Integer.parseInt(actual_out));


        Button dismiss = (Button) rootView.findViewById(R.id.button);
        dismiss.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
//                actual_in_update = ((NumberPicker) getView().findViewById(R.id.actual_in)).getValue();
//                actual_out_update = ((NumberPicker) getView().findViewById(R.id.actual_out)).getValue();

                processData(strtext);
                dismiss();
                ToastFactory.makeValidToast(getActivity(), "Success", "Your Record Updated.").show();
            }
        });
        return rootView;
    }
}