package &&&.XXXs.$$.UseCase;

import android.util.Log;

import org.json.simple.JSONObject;

import &&&.XXXs.$$.$$Service;

public class NextCommand extends NavigateCommand {

    NextCommand(JSONObject stepJson) {
        super(stepJson);
        Log.i($$Service.TAG, "Next Step");
    }

    public static boolean isNextAction(String action){
        return action.equals("next");
    }


    @Override
    public String toString() {
        return "NextStep{" +
                "State=" + getState().name() +
                '}';
    }
}
