package com.odoo.scan.product;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.orm.OModel;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
//import com.odoo.scan.deliveryorder.DOScannerFragment;
import com.odoo.scan.product.tasks.SearchProductBarcode;
import com.odoo.scan.models.ProductModel;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.drawer.DrawerItem;
import com.telly.groundy.Groundy;
import com.telly.groundy.annotations.OnSuccess;
import com.telly.groundy.annotations.Param;

import java.util.List;

/**
 * Created by bista on 24/8/15.
 */
public class DOBarcodeFragment extends BaseFragment implements IProcessData{

    private static final String TAG = DOBarcodeFragment.class.getSimpleName();
    public IOperationFlow mCallbacks = sDummyCallbacks;
    private static IOperationFlow sDummyCallbacks = new IOperationFlow() {

        @Override
        public void onValidFirstStep(Bundle args) {

        }

        @Override
        public void onOperationCancelled() {

        }

//        @Override
//        public void onProductScan() {
//
//        }

        @Override
        public void onStockMoveApproved(int id) {

        }

//        @Override
//        public void onStockMoveApproved(int id) {
//
//        }

        @Override
        public void onDOApproved() {

        }
    };

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
    public void onResume() {
        super.onResume();
    }

    @Override
    public void onPause() {
        super.onPause();
    }


    @Override
    public void onDetach() {
        super.onDetach();
        mCallbacks = sDummyCallbacks;
    }



    @OnSuccess(SearchProductBarcode.class)
    public void onSuccess(@Param("row") ODataRow result_do) {
        Bundle b = new Bundle();
        b.putSerializable("delivery_order", result_do);
        mCallbacks.onValidFirstStep(b);
    }

    @Override
    public void processData(String line) {
        Groundy.create(SearchProductBarcode.class)
                .callback(DOBarcodeFragment.this)
                .arg("serial", line)
                .queueUsing(getActivity().getApplicationContext());

    }

    @Override
    public void populateScreen(Bundle args) {

    }

    @Override
    public Object databaseHelper(Context context) {
        return new ProductModel(context);
    }

    @Override
    public void onSkidClicked(String product) {

    }

    @Override
    public List<DrawerItem> drawerMenus(Context context) {
        return null;
    }

    @Override
    public OModel db() {
        return new ProductModel(getActivity());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        setHasOptionsMenu(true);
        View rootView = inflater.inflate(R.layout.fragment_product, container, false);

        rootView.findViewById(R.id.scan_product).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                processData(((TextView) getView().findViewById(R.id.barcode_editText)).getText().toString());
            }
        });
        return rootView;
    }

}
