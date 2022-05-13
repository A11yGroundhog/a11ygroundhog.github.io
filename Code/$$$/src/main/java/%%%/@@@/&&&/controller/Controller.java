package &&&.XXXs.$$.controller;

import android.util.Log;

import org.json.simple.JSONObject;

import java.io.File;

import &&&.XXXs.$$.ActualWidgetInfo;
import &&&.XXXs.$$.Config;
import &&&.XXXs.$$.$$Service;
import &&&.XXXs.$$.UseCase.InfoCommand;
import &&&.XXXs.$$.UseCase.LocatableCommand;
import &&&.XXXs.$$.UseCase.NavigateCommand;
import &&&.XXXs.$$.UseCase.Command;
import &&&.XXXs.$$.Utils;
import &&&.XXXs.$$.WidgetInfo;

public class Controller {
    private final Locator locator;
    private final ActionPerformer actionPerformer;
    public Controller(Locator locator, ActionPerformer actionPerformer){
        this.locator = locator;
        this.actionPerformer = actionPerformer;
    }

    public void clearResult(){
        String dir = $$Service.getInstance().getBaseContext().getFilesDir().getPath();
        new File(dir, Config.v().CONTROLLER_RESULT_FILE_NAME).delete();
    }

    public void interrupt(){
        locator.interrupt();
    }

    public void executeCommand(String stepCommandJson){
        Command command = Command.createCommandFromJSON(stepCommandJson);
        executeCommand(command);
    }

    public void executeCommand(Command command){
        clearResult();
        if(command == null){
            Log.e($$Service.TAG, "The incoming Command is null!");
            writeResult(null);
            return;
        }

        command.setState(Command.CommandState.RUNNING);
        if(command instanceof LocatableCommand){
            executeLocatableStep((LocatableCommand) command);
        }
        else if (command instanceof NavigateCommand){
            navigate(command, (NavigateCommand) command);
        }
        else if (command instanceof InfoCommand){
            InfoCommand infoCommand = (InfoCommand) command;
            if(infoCommand.getQuestion().equals("a11y_focused")){
                WidgetInfo widgetInfo = ActualWidgetInfo.createFromA11yNode($$Service.getInstance().getAccessibilityFocusedNode());
                if (widgetInfo != null) {
                    Log.i($$Service.TAG, "The focused node is: " + widgetInfo + " Xpath: " + widgetInfo.getXpath());
                    JSONObject jsonCommand = widgetInfo.getJSONCommand("xpath", false, "click");
                    infoCommand.setJsonResult(jsonCommand);
                    infoCommand.setState(Command.CommandState.COMPLETED);
                }
                else{
                    Log.i($$Service.TAG, "The focused node is null! ");
                    infoCommand.setState(Command.CommandState.FAILED);
                }
            }
            else{
                infoCommand.setState(Command.CommandState.FAILED);
            }
            writeResult(infoCommand);
        }
        else{
            Log.e($$Service.TAG, "Unrecognizable Command!");
            writeResult(null);
        }
    }

    private void navigate(Command command, NavigateCommand navigateCommand) {
        ActionPerformer.ExecutorCallback callback = new ActionPerformer.ExecutorCallback() {
            @Override
            public void onCompleted() {
                onCompleted(null);
            }

            @Override
            public void onCompleted(ActualWidgetInfo navigatedWidget) {
                command.setState(Command.CommandState.COMPLETED);
                navigateCommand.setNavigatedWidget(navigatedWidget);
                writeResult(navigateCommand);
            }

            @Override
            public void onError(String message) {
                navigateCommand.setState(Command.CommandState.FAILED_PERFORM);
                Log.e($$Service.TAG, String.format("Error in navigating command %s. Message: %s", navigateCommand, message));
                writeResult(navigateCommand);
            }
        };
        try {
            actionPerformer.navigate(navigateCommand, callback);
        }
        catch (Exception e){
            navigateCommand.setState(Command.CommandState.FAILED);
            Log.e($$Service.TAG, String.format("An exception happened navigating command %s. Message: %s", navigateCommand, e.getMessage()));
            writeResult(navigateCommand);
        }
    }

    private void executeLocatableStep(LocatableCommand locatableCommand) {
        Locator.LocatorCallback locatorCallback = new Locator.LocatorCallback() {
            @Override
            public void onCompleted(ActualWidgetInfo actualWidgetInfo) {
                locatableCommand.setActedWidget(actualWidgetInfo);
                Log.i($$Service.TAG, String.format("Performing command %s on Widget %s", locatableCommand, actualWidgetInfo));
                actionPerformer.execute(locatableCommand, actualWidgetInfo, new ActionPerformer.ExecutorCallback() {
                    @Override
                    public void onCompleted() {
                        onCompleted(null);
                    }

                    @Override
                    public void onCompleted(ActualWidgetInfo navigatedWidget) {
                        locatableCommand.setState(Command.CommandState.COMPLETED);
                        writeResult(locatableCommand);
                    }

                    @Override
                    public void onError(String message) {
                        locatableCommand.setState(Command.CommandState.FAILED_PERFORM);
                        Log.e($$Service.TAG, String.format("Error in performing command %s. Message: %s", locatableCommand, message));
                        writeResult(locatableCommand);
                    }
                });
            }

            @Override
            public void onError(String message) {
                locatableCommand.setState(Command.CommandState.FAILED_LOCATE);
                Log.e($$Service.TAG, String.format("Error in locating command %s. Message: %s", locatableCommand, message));
                writeResult(locatableCommand);
            }
        };
        try {
            locator.locate(locatableCommand, locatorCallback);
        }
        catch (Exception e){
            locatableCommand.setState(Command.CommandState.FAILED);
            Log.e($$Service.TAG, String.format("An exception happened executing command %s. Message: %s", locatableCommand, e.getMessage()));
            writeResult(locatableCommand);
        }
    }

    private void writeResult(Command command){
        String jsonCommandStr = command != null ? command.getJSON().toJSONString() : "Error";
        Utils.createFile(Config.v().CONTROLLER_RESULT_FILE_NAME, jsonCommandStr);
    }
}
