package &&&.XXXs.$$.UseCase;

import android.util.Log;

import org.json.simple.JSONObject;

import &&&.XXXs.$$.$$Service;

public class PreviousCommand extends NavigateCommand {

    PreviousCommand(JSONObject stepJson) {
        super(stepJson);
        Log.i($$Service.TAG, "Previous Step");
    }

    public static boolean isPreviousAction(String action){
        return action.equals("previous");
    }


    @Override
    public String toString() {
        return "PreviousStep{" +
                "State=" + getState().name() +
                '}';
    }
}
