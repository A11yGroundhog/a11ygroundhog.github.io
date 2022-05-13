package &&&.XXXs.$$.controller;
import android.util.Pair;
import &&&.XXXs.$$.ActionUtils;
import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.UseCase.ClickCommand;

public class TouchActionPerformer extends BaseActionPerformer {
    @Override
    public boolean executeClick(ClickCommand clickStep, ActualWidgetInfo actualWidgetInfo) {
        Pair<Integer, Integer> clickableCoordinate = ActionUtils.getClickableCoordinate(actualWidgetInfo.getA11yNodeInfo(), true);
        return ActionUtils.performTap(clickableCoordinate);
    }
}
