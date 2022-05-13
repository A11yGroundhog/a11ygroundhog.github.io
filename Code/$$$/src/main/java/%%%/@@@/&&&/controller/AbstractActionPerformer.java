package &&&.XXXs.$$.controller;

import android.util.Log;
import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.$$Service;
import &&&.XXXs.$$.UseCase.ClickCommand;
import &&&.XXXs.$$.UseCase.FocusCommand;
import &&&.XXXs.$$.UseCase.LocatableCommand;
import &&&.XXXs.$$.UseCase.NavigateCommand;
import &&&.XXXs.$$.UseCase.NextCommand;
import &&&.XXXs.$$.UseCase.PreviousCommand;
import &&&.XXXs.$$.UseCase.SelectCommand;
import &&&.XXXs.$$.UseCase.TypeCommand;

public abstract class AbstractActionPerformer implements ActionPerformer {
    @Override
    public void navigate(NavigateCommand navigateCommand, ExecutorCallback callback) {
        if(callback == null)
            callback = new DummyExecutorCallback();
        if (navigateCommand instanceof NextCommand)
            navigateNext((NextCommand) navigateCommand, callback);
        else if (navigateCommand instanceof PreviousCommand)
            navigatePrevious((PreviousCommand) navigateCommand, callback);
        else if (navigateCommand instanceof SelectCommand)
            navigateSelect((SelectCommand) navigateCommand, callback);
        else {
            Log.e($$Service.TAG, "This navigate step is unrecognizable " + navigateCommand);
            callback.onError("Unrecognizable Action");
        }
    }

    @Override
    public final void execute(LocatableCommand locatableCommand, ActualWidgetInfo actualWidgetInfo, ExecutorCallback callback) {
        if(callback == null)
            callback = new DummyExecutorCallback();
        Log.i($$Service.TAG, this.getClass().getSimpleName() + " executing " + locatableCommand);
        boolean actionResult = false;
        if (locatableCommand == null || actualWidgetInfo == null){
            Log.e($$Service.TAG, String.format("Problem with locatable step %s or actualWidgetInfo %s", locatableCommand, actualWidgetInfo));
            callback.onError("Error in parameters");
            return;
        }
        if(locatableCommand instanceof ClickCommand) {
            actionResult = executeClick((ClickCommand) locatableCommand, actualWidgetInfo);
        }
        else if(locatableCommand instanceof TypeCommand) {
            actionResult = executeType((TypeCommand) locatableCommand, actualWidgetInfo);
        }
        else if(locatableCommand instanceof FocusCommand){
            actionResult = executeFocus((FocusCommand) locatableCommand, actualWidgetInfo);
        }
        else {
            Log.e($$Service.TAG, "This locatable step is unrecognizable " + locatableCommand);
            callback.onError("Unrecognizable Action");
            return;
        }
        if(actionResult){
            Log.i($$Service.TAG, "Action is executed successfully!");
            callback.onCompleted();
        }
        else{
            Log.i($$Service.TAG, "Action could not be executed!");
            callback.onError("Error on execution!");
        }
    }

    public abstract boolean executeClick(ClickCommand clickStep, ActualWidgetInfo actualWidgetInfo);
    public abstract boolean executeType(TypeCommand typeStep, ActualWidgetInfo actualWidgetInfo);
    public abstract boolean executeFocus(FocusCommand focusStep, ActualWidgetInfo actualWidgetInfo);
    public abstract void navigateNext(NextCommand nextStep, ExecutorCallback callback);
    public abstract void navigatePrevious(PreviousCommand previousStep, ExecutorCallback callback);
    public abstract void navigateSelect(SelectCommand selectCommand, ExecutorCallback callback);
}
