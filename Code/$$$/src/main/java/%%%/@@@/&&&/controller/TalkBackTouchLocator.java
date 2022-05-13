package &&&.XXXs.$$.controller;

import android.util.Log;
import android.util.Pair;

import &&&.XXXs.$$.ActionUtils;
import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.ConceivedWidgetInfo;
import &&&.XXXs.$$.$$Service;

public class TalkBackTouchLocator extends BaseLocator{
    @Override
    protected LocatorResult locateAttempt(ConceivedWidgetInfo targetWidget) {
        LocatorResult result = super.locateAttempt(targetWidget);
        if(result.status != LocatorStatus.COMPLETED)
            return result;
        ActualWidgetInfo actualWidgetInfo = result.actualWidgetInfo;
        if(!ActionUtils.isFocusedNodeTarget(actualWidgetInfo.getA11yNodeInfo())){
            Pair<Integer, Integer> clickableCoordinate = ActionUtils.getClickableCoordinate(actualWidgetInfo.getA11yNodeInfo(), true);
            ActionUtils.performTap(clickableCoordinate);
            return new LocatorResult(LocatorStatus.WAITING);
        }
        return new LocatorResult(actualWidgetInfo);
    }
}
