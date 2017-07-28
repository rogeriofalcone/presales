package com.odoo.scan;

import android.content.Context;
import android.os.Bundle;

public interface IProcessData {
    void processData(String line);
    void populateScreen(Bundle args);

    Object databaseHelper(Context context);

    void onSkidClicked(String product);
}
