/** ##############################################################################
 #
 #    OpenERP, Open Source Management Solution
 #    This module copyright (C) 2014 Savoir-faire Linux
 #    (<http://www.savoirfairelinux.com>).
 #
 #    Authors: Alexandre Lision alexandre.lision@savoirfairelinux.com
 #
 #    This program is free software: you can redistribute it and/or modify
 #    it under the terms of the GNU Affero General Public License as
 #    published by the Free Software Foundation, either version 3 of the
 #    License, or (at your option) any later version.
 #
 #    This program is distributed in the hope that it will be useful,
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #    GNU Affero General Public License for more details.
 #
 #    You should have received a copy of the GNU Affero General Public License
 #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 #
 ############################################################################## */

package com.odoo.scan;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Parcelable;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import com.odoo.BaseActivity;
import com.odoo.crm.R;
import com.odoo.orm.OSyncHelper;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.product.DOBarcodeFragment;
import com.odoo.scan.product.ProductFragment;
import com.odoo.scan.stockroute.StockRouteFragment;
import com.odoo.scan.views.StuckViewPager;
import com.odoo.support.OUser;
import com.odoo.support.fragment.BaseFragment;
import com.odoo.util.ToastFactory;
import com.odoo.util.drawer.DrawerItem;
import com.telly.groundy.GroundyManager;
import odoo.OArguments;
import org.json.JSONArray;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

import com.intermec.aidc.*;


public class PagerFragment extends BaseFragment implements IOperationFlow, BarcodeReadListener{
    StuckViewPager mViewPager;
    SectionsPagerAdapter mSectionsPagerAdapter;
    public static final String TAG = PagerFragment.class.getSimpleName();
    TextView mTextScannerState;
    private boolean isWaitingForOperation;
    TYPE mType;

    private static final String DATA_STRING_TAG = "com.motorolasolutions.emdk.datawedge.data_string";
    private static final String INTENT_ACTION = "com.odoo.MainActivity.RECVR";

    static int REQUEST_ENABLE_BT = 239; // random number

    private static final Field sChildFragmentManagerField;

    private com.intermec.aidc.BarcodeReader bcr;

    static {
        Field f = null;
        try {
            f = Fragment.class.getDeclaredField("mChildFragmentManager");
            f.setAccessible(true);
        } catch (NoSuchFieldException e) {
            Log.e(TAG, "Error getting mChildFragmentManager field", e);
        }
        sChildFragmentManagerField = f;
    }

    @Override
    public void barcodeRead(BarcodeReadEvent aBarcodeReadEvent)
    {
        String data = aBarcodeReadEvent.getBarcodeData();
        onDataReceived(data);
    }

    BroadcastReceiver mReceiver;

    public class MyReceiver extends BroadcastReceiver {

        @Override
        public void onReceive(Context context, Intent intent) {
            if ( intent.getAction().contentEquals(INTENT_ACTION) ) {
                String data = intent.getStringExtra(DATA_STRING_TAG);
                onDataReceived(data);
            }
        }
    }

    public enum TYPE {
        STOCKMOVE,
        DO,
        RECEIVE,
        PRODUCT
    }

    public static PagerFragment newInstance(TYPE t) {
        PagerFragment frag = new PagerFragment();

        Bundle args = new Bundle();
        args.putSerializable("TYPE", t);
        frag.setArguments(args);

        return frag;
    }

    @Override
    public Object databaseHelper(Context context) {
        return new DeliveryCylinderModel(context);
    }

    @Override
    public void onAttach(Activity activity) {
        super.onAttach(activity);
    }

    @Override
    public void onDetach() {
        super.onDetach();
        GroundyManager.cancelAll(getActivity());
        if (sChildFragmentManagerField != null) {
            try {
                sChildFragmentManagerField.set(this, null);
            } catch (Exception e) {
                Log.e(TAG, "Error setting mChildFragmentManager field", e);
            }
        }
    }

    @Override
    public void onCreate(Bundle savedBundle) {
        super.onCreate(savedBundle);
        try {
            //get bar code instance from MainActivity
            bcr = BaseActivity.getBarcodeObject();

            if(bcr != null)
            {
                //enable scanner
                bcr.setScannerEnable(true);

                //set listener
                bcr.addBarcodeReadListener(this);
            }

        } catch (BarcodeReaderException e) {
            e.printStackTrace();
        }
        isWaitingForOperation = true;
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {

        mType = (TYPE) getArguments().getSerializable("TYPE");
        mSectionsPagerAdapter = new SectionsPagerAdapter(getActivity(), getChildFragmentManager());

        View rootView = inflater.inflate(R.layout.fragment_pager, container, false);
        // Set up the ViewPager with the sections adapter.
        mViewPager = (StuckViewPager) rootView.findViewById(R.id.pager);

        mViewPager.setOffscreenPageLimit(1);
        mViewPager.setAdapter(mSectionsPagerAdapter);
        mViewPager.setPagingEnabled(false);
        mViewPager.setCurrentItem(0);

        return rootView;
    }

    @Override
    public void onResume() {
        super.onResume();
        mReceiver = new MyReceiver();
        getActivity().registerReceiver(mReceiver, new IntentFilter(INTENT_ACTION));
    }

    @Override
    public void onPause() {
        super.onPause();
        getActivity().unregisterReceiver(mReceiver);
    }

    @Override
    public List<DrawerItem> drawerMenus(Context context) {
        return null;
    }

    @Override
    public void onValidFirstStep(Bundle args) {
//        ((TextView) getView().findViewById(R.id.top_message_textView)).setText(R.string.scanlabel_skids);
        ((IProcessData) mSectionsPagerAdapter.getItem(1)).populateScreen(args);
        mViewPager.setCurrentItem(1);
        isWaitingForOperation = false;
    }

    @Override
    public void onOperationCancelled() {
        isWaitingForOperation = true;
        ((TextView) getView().findViewById(R.id.top_message_textView)).setText(R.string.scanlabel_delivery_order);
        mViewPager.setCurrentItem(0);
    }

    @Override
    public void onStockMoveApproved(final int stockID) {
        Runnable tryIt = new Runnable() {
            @Override
            public void run() {
//            	Context context = getActivity();
//                StockMoveModel model = new StockMoveModel(context);
//
//                OUser user = OUser.current(context);
//                OSyncHelper oSyncHelper = new OSyncHelper(context, user, model);
//                try {
//                    OArguments args = new OArguments();
//                    args.add(new JSONArray().put(stockID));
//                    Boolean result = (Boolean) oSyncHelper.callMethod("action_done", args);
//
//                    if (result) {
//                    	ToastFactory.makeErrorToast(context, "StockMove correctly processed", "").show();
//                    } else {
//                        ToastFactory.makeErrorToast(getActivity(), "Error processing stockmove", "Please verify your internet connection").show();
//                    }
//
//                }catch(Exception e){
//                	e.printStackTrace();
//                	ToastFactory.makeErrorToast(getActivity(), "Error processing stockmove", "Please verify your internet connection").show();
//              }
            }
        };
        tryIt.run();
        mViewPager.setCurrentItem(0);
        isWaitingForOperation = true;
    }

    @Override
    public void onDOApproved() {
        mViewPager.setCurrentItem(0);
        isWaitingForOperation = true;
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            Log.i(TAG, "We were in settings");
        }
    }

    @Override
    public void onStart() {
        super.onStart();
    }


    public class SectionsPagerAdapter extends android.support.v4.app.FragmentStatePagerAdapter {

        private final String TAG = SectionsPagerAdapter.class.getSimpleName();
        Context mContext;
        ArrayList<Fragment> fragments;

        public SectionsPagerAdapter(Context c, FragmentManager fm) {
            super(fm);
            mContext = c;
            fragments = new ArrayList<Fragment>();
            switch (mType) {
                case DO:
                    fragments.add(new StockRouteFragment());

            }
        }

        @Override
        public Fragment getItem(int i) {
            return fragments.get(i);
        }

        @Override
        public int getCount() {
            return fragments.size();
        }

        @Override
        public void restoreState(Parcelable arg0, ClassLoader arg1) {
            //do nothing here! no call to super.restoreState(arg0, arg1);
        }
    }

    public void onDataReceived(final String line) {
        getActivity().runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if(isWaitingForOperation) {
                    ((IProcessData) mSectionsPagerAdapter.getItem(0)).processData(line);
                } else{
                    ((IProcessData) mSectionsPagerAdapter.getItem(1)).processData(line);
                }
            }
        });
    }

}