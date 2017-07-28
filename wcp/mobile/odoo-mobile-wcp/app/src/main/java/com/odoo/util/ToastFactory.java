package com.odoo.util;

import android.content.Context;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import com.odoo.crm.R;


public class ToastFactory {

    public static Toast makeValidToast(Context con, String title, String subtitle){
        View layout = LayoutInflater.from(con).inflate(R.layout.toast_valid, null);

        Toast toast = new Toast(con);
        toast.setGravity(Gravity.CENTER_VERTICAL, 0, 0);
        toast.setDuration(Toast.LENGTH_LONG);
        ((TextView)layout.findViewById(R.id.toast_title)).setText(title);
        ((TextView)layout.findViewById(R.id.toast_subtitle)).setText(subtitle);

        toast.setView(layout);
        return toast;
    }

    public static Toast makeErrorToast(Context con, String title, String subtitle){
        View layout = LayoutInflater.from(con).inflate(R.layout.toast_error, null);

        Toast toast = new Toast(con);
        toast.setGravity(Gravity.CENTER_VERTICAL, 0, 0);
        toast.setDuration(Toast.LENGTH_LONG);
        ((TextView)layout.findViewById(R.id.toast_title)).setText(title);
        ((TextView)layout.findViewById(R.id.toast_subtitle)).setText(subtitle);

        toast.setView(layout);
        return toast;
    }
}
