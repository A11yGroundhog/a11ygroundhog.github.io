package &&&.XXXs.$$.UseCase;

import android.util.Log;

import org.json.simple.JSONObject;

import &&&.XXXs.$$.$$Service;

public class SleepCommand extends Command {
    private long sleepTime;

    SleepCommand(JSONObject stepJson) {
        super(stepJson);
        long sleepTime = Long.parseLong((String) stepJson.getOrDefault("sleep", "-1"));
        if(sleepTime == -1) {
            Log.e($$Service.TAG, "Issue with sleep step " + stepJson);
            sleepTime = 0;
        }
        this.sleepTime = sleepTime;
        Log.i($$Service.TAG, "Sleep Step: " + this.sleepTime);
    }

    public static boolean isSleepAction(String action){
        return action.equals("sleep");
    }

    public long getSleepTime() {
        return sleepTime;
    }

    @Override
    public String toString() {
        return "SleepStep{" +
                "State=" + getState().name() +
                "sleepTime=" + sleepTime +
                '}';
    }
}
