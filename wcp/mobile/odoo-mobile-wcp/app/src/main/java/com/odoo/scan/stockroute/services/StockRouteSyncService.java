package com.odoo.scan.stockroute.services;

import android.accounts.Account;
import android.app.Service;
import android.content.AbstractThreadedSyncAdapter;
import android.content.ContentProviderClient;
import android.content.Context;
import android.content.Intent;
import android.content.SyncResult;
import android.os.Bundle;
import android.os.Debug;
import android.os.IBinder;
import android.util.Log;

import com.odoo.auth.OdooAccountManager;
import com.odoo.orm.OSyncHelper;
import com.odoo.receivers.SyncFinishReceiver;
import com.odoo.scan.models.DeliveryCylinderModel;
import com.odoo.scan.models.StockRouteModel;

/**
 * Created by bista on 28/12/15.
 */
public class StockRouteSyncService extends Service {

    public static final String TAG = StockRouteSyncService.class.getSimpleName();
    private static SyncAdapterImpl sSyncAdapter = null;
    Context mContext = null;

    public StockRouteSyncService() {
        mContext = this;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return getSyncAdapter().getSyncAdapterBinder();
    }

    public SyncAdapterImpl getSyncAdapter() {

        if (sSyncAdapter == null) {
            sSyncAdapter = new SyncAdapterImpl(this);
        }
        return sSyncAdapter;
    }

    public void performSync(Context context, Account account, Bundle extras,
                            String authority, ContentProviderClient provider,
                            SyncResult syncResult) {
        Debug.startMethodTracing("synclog");
        Intent intent = new Intent();
        intent.setAction(SyncFinishReceiver.SYNC_FINISH);

        StockRouteModel db = new StockRouteModel(context);
        db.setUser(OdooAccountManager.getAccountDetail(context,
                account.name));
        OSyncHelper odooSyncHelper = db.getSyncHelper();

        //ODomain domain = new ODomain();
        //domain.add(ProductModel.fields.STATE, "=", "assigned");

        if (odooSyncHelper != null && odooSyncHelper.syncWithServer()) {
            if (OdooAccountManager.currentUser(context).getAndroidName().equals(account.name))
                context.sendBroadcast(intent);
        }
        //Debug.stopMethodTracing();
    }


    public class SyncAdapterImpl extends AbstractThreadedSyncAdapter {
        private Context mContext;

        public SyncAdapterImpl(Context context) {
            super(context, true);
            mContext = context;
        }

        @Override
        public void onPerformSync(Account account, Bundle bundle, String str,
                                  ContentProviderClient providerClient, SyncResult syncResult) {
            Log.d(TAG, "StockSyncService started");
            if (account != null) {
                new StockRouteSyncService().performSync(mContext, account,
                        bundle, str, providerClient, syncResult);
            }
        }
    }
}
