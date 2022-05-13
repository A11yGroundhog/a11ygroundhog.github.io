package &&&.XXXs.$$.UseCase;

import android.util.Log;

import org.json.simple.JSONObject;

import &&&.XXXs.$$.$$Service;

public class SelectCommand extends NavigateCommand {

    SelectCommand(JSONObject stepJson) {
        super(stepJson);
        Log.i($$Service.TAG, "Select Command");
    }

    public static boolean isSelectCommand(String action){
        return action.equals("select");
    }


    @Override
    public String toString() {
        return "SelectStep{" +
                "State=" + getState().name() +
                '}';
    }
}
