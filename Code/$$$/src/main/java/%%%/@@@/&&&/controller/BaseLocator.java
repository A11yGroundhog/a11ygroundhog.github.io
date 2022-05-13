package &&&.XXXs.$$.controller;

import android.util.Log;

import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.ConceivedWidgetInfo;
import &&&.XXXs.$$.$$Service;

public class BaseLocator extends AbstractLocator {
    @Override
    protected LocatorResult locateAttempt(ConceivedWidgetInfo targetWidget)
    {
        ActualWidgetInfo actualWidgetInfo = findActualWidget(targetWidget);
        if(actualWidgetInfo == null){
            Log.i($$Service.TAG, "The target widget could not be found at this moment!");
            return new LocatorResult(LocatorStatus.WAITING);
        }
        return new LocatorResult(actualWidgetInfo);
    }
}
