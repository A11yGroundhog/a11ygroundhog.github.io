package &&&.XXXs.$$.controller;

import android.util.Log;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.zip.Deflater;

import &&&.XXXs.$$.ActionUtils;
import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.$$Service;
import &&&.XXXs.$$.UseCase.ClickCommand;
import &&&.XXXs.$$.UseCase.FocusCommand;
import &&&.XXXs.$$.UseCase.NextCommand;
import &&&.XXXs.$$.UseCase.PreviousCommand;
import &&&.XXXs.$$.UseCase.SelectCommand;
import &&&.XXXs.$$.UseCase.TypeCommand;

public class TalkBackActionPerformer extends BaseActionPerformer {
    static class TalkBackActionCallback implements ActionUtils.ActionCallback{
        private ExecutorCallback callback;
        TalkBackActionCallback(ExecutorCallback callback){
            if (callback == null)
                this.callback = new DummyExecutorCallback();
            this.callback = callback;
        }
        @Override
        public void onCompleted(AccessibilityNodeInfo nodeInfo) {
            callback.onCompleted(ActualWidgetInfo.createFromA11yNode(nodeInfo));
        }

        @Override
        public void onError(String message) {
            callback.onError(message);
        }
    }

    private boolean isNotFocused(ActualWidgetInfo actualWidgetInfo) {
        if(!ActionUtils.isFocusedNodeTarget(actualWidgetInfo.getA11yNodeInfo())){
            Log.e($$Service.TAG, String.format("The focused node %s is different from target node %s", $$Service.getInstance().getAccessibilityFocusedNode(), actualWidgetInfo));
            return true;
        }
        return false;
    }

    @Override
    public boolean executeClick(ClickCommand clickStep, ActualWidgetInfo actualWidgetInfo) {
        if (isNotFocused(actualWidgetInfo))
            return false;
        return ActionUtils.performDoubleTap();
    }

    @Override
    public boolean executeType(TypeCommand typeStep, ActualWidgetInfo actualWidgetInfo) {
        if (isNotFocused(actualWidgetInfo))
            return false;
        return super.executeType(typeStep, actualWidgetInfo);
    }

    @Override
    public boolean executeFocus(FocusCommand focusStep, ActualWidgetInfo actualWidgetInfo) {
        if (isNotFocused(actualWidgetInfo))
            return false;
        return super.executeFocus(focusStep, actualWidgetInfo);
    }

    @Override
    public void navigateNext(NextCommand nextStep, ExecutorCallback callback) {
        ActionUtils.swipeRight(new TalkBackActionCallback(callback));
    }

    @Override
    public void navigatePrevious(PreviousCommand previousStep, ExecutorCallback callback) {
        ActionUtils.swipeLeft(new TalkBackActionCallback(callback));
    }

    @Override
    public void navigateSelect(SelectCommand selectCommand, ExecutorCallback callback) {
        if(callback == null)
            callback = new DummyExecutorCallback();
        AccessibilityNodeInfo focusedNode = $$Service.getInstance().getAccessibilityFocusedNode();
        ExecutorCallback finalCallback = callback;
        ActionUtils.performDoubleTap(new ActionUtils.ActionCallback() {
            @Override
            public void onCompleted(AccessibilityNodeInfo nodeInfo) {
                finalCallback.onCompleted(ActualWidgetInfo.createFromA11yNode(focusedNode));
            }

            @Override
            public void onError(String message) {
                finalCallback.onError(message);
            }
        });
    }
}
