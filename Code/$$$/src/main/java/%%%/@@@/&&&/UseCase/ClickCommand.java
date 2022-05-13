package &&&.XXXs.$$.UseCase;

import android.util.Log;

import org.json.simple.JSONObject;

import &&&.XXXs.$$.$$Service;

public class ClickCommand extends LocatableCommand {
    ClickCommand(JSONObject stepJson) {
        super(stepJson);
        Log.i($$Service.TAG, "Clickable Step: " + this.getTargetWidgetInfo());
    }
    public static boolean isClickStep(String action){
        return action.equals("click");
    }


    @Override
    public String toString() {
        return String.format("ClickStep{State=%s,WidgetTarget=%s}", getState(), getTargetWidgetInfo());
    }
}
