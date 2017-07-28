package com.odoo.scan;

import com.odoo.crm.R;

import java.io.Serializable;
import java.util.HashMap;

public class PlannedMove implements Serializable {
    private String productID;
    private int planned; //quantity planned to be moved
    private int picked; //quantity already picked
    public HashMap<String, Integer> pickedMovesMap;

    public PlannedMove(String productID, Integer planned) {
        this.productID = productID;
        this.planned = planned;
        picked = 0;
        pickedMovesMap = new HashMap<String, Integer>();
    }

    public String getProductID(){
        return productID;
    }

    public boolean isFilled(){
        return (picked > 0 && picked == planned);
    }

    public boolean isPartial(){
        return picked > 0 && picked < planned;
    }

    public String getPickedOverTotal(){
        return picked + "/" + planned;
    }

    public int getColor(){
        if (picked > 0 && picked < planned) {
            return R.color.holo_orange_light;
        }
        if (isFilled()) {
            return R.color.holo_green_light;
        }
        return R.color.white;
    }

    public int getPicked() {
        return picked;
    }

    public int getPlanned(){
        return planned;
    }

    public String addPickedMove(String stockmoveID, Integer quantity) {
        if(pickedMovesMap.containsKey(stockmoveID))
            return "Skid already scanned";
        if(quantity > planned - picked)
            return "Quantity superior please contact your manager";
        pickedMovesMap.put(stockmoveID, quantity);
        picked += quantity;
        return null;
    }
}
