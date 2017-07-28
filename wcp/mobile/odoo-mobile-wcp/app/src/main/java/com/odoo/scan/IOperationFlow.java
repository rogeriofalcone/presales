package com.odoo.scan;

import android.os.Bundle;

public interface IOperationFlow {

    public void onValidFirstStep(Bundle args);
    public void onOperationCancelled();

    public void onStockMoveApproved(int id);
    public void onDOApproved();
}
