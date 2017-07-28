package com.odoo.scan.product;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v4.view.ViewPager;
import android.support.v7.widget.GridLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.odoo.MainActivity;
import com.odoo.crm.R;
import com.odoo.orm.ODataRow;
import com.odoo.scan.IOperationFlow;
import com.odoo.scan.IProcessData;
import com.odoo.scan.models.ProductModel;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.drawer.DrawerItem;

import java.util.List;

/**
 * Created by bista on 24/8/15.
 */
public class ProductFragment extends BaseFragment implements IProcessData, ProductAdapter.ProductViewHolder.ISkidClick {

    public static final String TAG = ProductFragment.class.getSimpleName();
    private RecyclerView mRecyclerView;
    private GridLayoutManager mLayoutManager;
    private ViewPager mViewPager;
    private ProductAdapter mAdapter;
    TextView mDONameTextView;
    TextView mDOQuantityTextView;
    TextView mDOOutgoingQtyTextView;
    TextView mDOIncommingQtyTextView;
    TextView mDOPriceTextView;
    TextView mDOWeightTextView;
    TextView mDODefautCodeTextView;
    TextView mDORow;
    TextView mDORack;
    TextView mDOCase;

    private ODataRow mProcessingDO;

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
    public void processData(String line) {

    }

    @Override
    public void populateScreen(Bundle args) {
        mProcessingDO = (ODataRow) args.getSerializable("delivery_order");

        mDONameTextView.setText(mProcessingDO.getString(ProductModel.fields.NAME));
        mDOQuantityTextView.setText(mProcessingDO.getString(ProductModel.fields.QUNATITY));
        mDOPriceTextView.setText(mProcessingDO.getString(ProductModel.fields.LIST_PRICE));
        mDODefautCodeTextView.setText(mProcessingDO.getString(ProductModel.fields.DEFAULT_CODE));
        mAdapter.notifyDataSetChanged();
    }

    @Override
    public Object databaseHelper(Context context) {
        return new ProductModel(context);
    }

    @Override
    public List<DrawerItem> drawerMenus(Context context) {
        return null;
    }

    @Override
    public void onSkidClicked(String product) {

    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mAdapter = new ProductAdapter(getActivity(),this);
    }

    @Override
    public View onCreateView(final LayoutInflater inflater, final ViewGroup container, Bundle savedInstanceState) {
        final View rootView = inflater.inflate(R.layout.item_product, container, false);

        //final View productView = inflater.inflate(R.layout.fragment_product, container, false);

        mRecyclerView = (RecyclerView) rootView.findViewById(R.id.skids_grid);

        mDONameTextView = (TextView) rootView.findViewById(R.id.do_name);
        mDOQuantityTextView = (TextView) rootView.findViewById(R.id.do_quantity);
//        mDOPriceTextView = (TextView) rootView.findViewById(R.id.do_lst_price);
        mDOIncommingQtyTextView = (TextView) rootView.findViewById(R.id.incomming_qty);
        mDOOutgoingQtyTextView = (TextView)rootView.findViewById(R.id.outgoing_qty);
        mDOWeightTextView = (TextView) rootView.findViewById(R.id.gross_weight);
        mDODefautCodeTextView = (TextView)rootView.findViewById(R.id.default_code);
//        mDOCase = (TextView)rootView.findViewById(R.id.loc_case);
//        mDORow = (TextView)rootView.findViewById(R.id.loc_row);
//        mDORack = (TextView)rootView.findViewById(R.id.loc_rack);

        mLayoutManager = new GridLayoutManager(getActivity(), 2);
        mRecyclerView.setLayoutManager(mLayoutManager);
        mRecyclerView.setAdapter(mAdapter);
    //        mSectionsPagerAdapter = new PagerFragment.SectionsPagerAdapter(getActivity(), getChildFragmentManager());
        //mRecyclerView.setLayoutManager(mLayoutManager);

        rootView.findViewById(R.id.button_product_cancel).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                    //mCallbacks.onDOApproved();
                //Intent myIntent = new Intent(getActivity(), MainActivity.class);
                //getActivity().startActivity(myIntent);

                DOBarcodeFragment fragment2 = new DOBarcodeFragment();
                Intent intent = new Intent(getActivity(), MainActivity.class);
                ProductFragment.this.startActivity(intent);

               // getActivity().getSupportFragmentManager().popBackStack(0);
                //getActivity().getSupportFragmentManager().beginTransaction().remove(ProductFragment.this).commit();
                //RelativeLayout layout = (RelativeLayout) rootView.findViewById(R.id.item_product);
                //layout.removeAllViewsInLayout();
               // FragmentTransaction ft = getFragmentManager().beginTransaction();
                //ft.add(R.id.product_scanner, fragment2);
               // ft.commit();
//                getFragmentManager()
//                        .beginTransaction()
//                        .addToBackStack(fragment2)
//                        .commit();
                // mViewPager.setCurrentItem(0);
//                FragmentManager fragmentManager = getActivity().getSupportFragmentManager();
//                FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
//                fragmentTransaction.replace(R.id.item_product, fragment2);
//                fragmentTransaction.addToBackStack(null);
//                fragmentTransaction.commit();
                return;
                }
        });

        return rootView;
    }

}
