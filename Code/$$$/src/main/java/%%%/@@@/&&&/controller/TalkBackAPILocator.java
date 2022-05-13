package &&&.XXXs.$$.controller;

import android.util.Log;

import &&&.XXXs.$$.ActionUtils;
import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.ConceivedWidgetInfo;
import &&&.XXXs.$$.$$Service;

public class TalkBackAPILocator extends BaseLocator{
    @Override
    protected LocatorResult locateAttempt(ConceivedWidgetInfo targetWidget) {
        LocatorResult result = super.locateAttempt(targetWidget);
        if(result.status != LocatorStatus.COMPLETED)
            return result;
        ActualWidgetInfo actualWidgetInfo = result.actualWidgetInfo;
        if(!ActionUtils.isFocusedNodeTarget(actualWidgetInfo.getA11yNodeInfo())){
            Log.e($$Service.TAG, String.format("API Focusing on %s", actualWidgetInfo.getA11yNodeInfo()));
            ActionUtils.a11yFocusOnNode(actualWidgetInfo.getA11yNodeInfo());
            return new LocatorResult(LocatorStatus.WAITING);
        }
        return new LocatorResult(actualWidgetInfo);
    }
}
