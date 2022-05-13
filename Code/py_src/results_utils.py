import logging
import asyncio
import json
import datetime
import shutil
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Dict, List, Tuple

from GUI_utils import Node, bounds_included, is_in_same_state_with_layout_path, NodesFactory
from adb_utils import get_current_activity_name, get_windows, get_activities, capture_layout as adb_capture_layout
from command import LocatableCommandResponse
from consts import ---_%%%_TAG, ---_%%%_EVENTS_TAG
from json_util import JSONSerializable
from $$_executor_utils import ExecutionResult, $$_capture_layout as capture_layout
from padb_utils import ParallelADBLogger, save_screenshot
from utils import annotate_rectangle

logger = logging.getLogger(__name__)

class AddressBook:
    BASE_MODE = "base"
    INITIAL = "INITIAL"
    ## Audits
    TALKBACK_EXPLORE = "talkback_explore"
    PROCESS_SCREENSHOT = "process_screenshot"
    EXTRACT_ACTIONS = "extract_actions"
    PERFORM_ACTIONS = "perform_actions"

    def __init__(self, snapshot_result_path: Union[Path, str]):
        if isinstance(snapshot_result_path, str):
            snapshot_result_path = Path(snapshot_result_path)
        # ---- For Web Visualization ------
        self.whelper = WebHelper(self)
        # --------------

        self.snapshot_result_path = snapshot_result_path
        self.audit_path_map = {}
        # ----------- Audit: talkback_explore ---------------
        self.audit_path_map[AddressBook.TALKBACK_EXPLORE] = self.snapshot_result_path.joinpath("TalkBackExplore")
        self.tb_explore_all_nodes_screenshot = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath(
            "all_nodes.png")
        self.tb_explore_android_log = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath("android.log")
        self.tb_explore_android_events_log = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath(
            "android_events.log")
        self.tb_explore_visited_nodes_path = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath(
            "visited_nodes.jsonl")
        self.tb_explore_visited_nodes_screenshot = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath(
            "visited_nodes.png")
        self.tb_explore_visited_nodes_gif = self.audit_path_map[AddressBook.TALKBACK_EXPLORE].joinpath(
            "visited_nodes.gif")
        # ----------- Audit: Process Snapshot (OCR) ---------------
        self.audit_path_map[AddressBook.PROCESS_SCREENSHOT] = self.snapshot_result_path.joinpath("ProcessSnapshot")
        # ----------- Audit: Extract Actions ---------------
        self.audit_path_map[AddressBook.EXTRACT_ACTIONS] = self.snapshot_result_path.joinpath("ExtractActions")
        self.extract_actions_modes = {Actionables.All: 'all_actionables',
                                      Actionables.UniqueResource: 'unique_resource_actionables',
                                      Actionables.NA11y: 'na11y_actionables',
                                      Actionables.TBReachable: 'tb_reachable_actionables',
                                      Actionables.TBUnreachable: 'tb_unreachable_actionables',
                                      Actionables.Selected: 'selected_actionables',
                                      Actionables.Spanned: 'spanned_actionables',
                                      }
        self.extract_actions_nodes = {}
        self.extract_actions_screenshots = {}
        for mode, value in self.extract_actions_modes.items():
            self.extract_actions_nodes[mode] = self.audit_path_map[
                AddressBook.EXTRACT_ACTIONS].joinpath(f"{value}.jsonl")
            self.extract_actions_screenshots[mode] = self.audit_path_map[
                AddressBook.EXTRACT_ACTIONS].joinpath(f"{value}.png")
        # ----------- Audit: perform_actions ---------------
        self.audit_path_map[AddressBook.PERFORM_ACTIONS] = self.snapshot_result_path.joinpath("PerformActions")
        self.perform_actions_results_path = self.audit_path_map[AddressBook.PERFORM_ACTIONS].joinpath("results.jsonl")
        self.perform_actions_atf_issues_path = self.audit_path_map[AddressBook.PERFORM_ACTIONS].joinpath(
            "atf_elements.jsonl")
        self.perform_actions_atf_issues_screenshot = self.audit_path_map[AddressBook.PERFORM_ACTIONS].joinpath(
            "atf_elements.png")
        self.perform_actions_summary = self.audit_path_map[AddressBook.PERFORM_ACTIONS].joinpath(
            "summary_of_actions_v2.jsonl")
        # ---------------------------------------------------
        # TODO: Needs to find a more elegant solution
        navigate_modes = [AddressBook.BASE_MODE, "tb_touch", "touch", "a11y_api"]
        self.mode_path_map = {}
        for mode in navigate_modes:
            self.mode_path_map[mode] = self.snapshot_result_path.joinpath(mode)
        self.initiated_path = self.snapshot_result_path.joinpath("initiated.txt")
        self.ovsersight_path = self.snapshot_result_path.joinpath("OS")
        # self.atf_issues_path = self.mode_path_map['exp'].joinpath("atf_issues.jsonl")
        self.action_path = self.snapshot_result_path.joinpath("action.jsonl")
        # self.all_element_screenshot = self.mode_path_map['exp'].joinpath("all_elements.png")
        # self.atf_issues_screenshot = self.mode_path_map['exp'].joinpath("atf_elements.png")
        # self.all_action_screenshot = self.mode_path_map['exp'].joinpath("all_actions.png")
        # self.valid_action_screenshot = self.mode_path_map['exp'].joinpath("valid_actions.png")
        # self.redundant_action_screenshot = self.mode_path_map['exp'].joinpath("redundant_actions.png")
        # self.visited_action_screenshot = self.mode_path_map['exp'].joinpath("visited_actions.png")
        # self.visited_elements_screenshot = self.mode_path_map['exp'].joinpath("visited_elements.png")
        # self.visited_elements_gif = self.mode_path_map['exp'].joinpath("visited_elements.gif")
        self.finished_path = self.snapshot_result_path.joinpath("finished.flag")
        # self.last_explore_log_path = self.snapshot_result_path.joinpath("last_explore.log")
        self.visited_elements_path = self.snapshot_result_path.joinpath("visited.jsonl")
        # self.valid_elements_path = self.snapshot_result_path.joinpath("valid_elements.jsonl")
        self.tags_path = self.snapshot_result_path.joinpath("tags.jsonl")
        self.note_path = self.snapshot_result_path.joinpath("note.txt")
        # self.s_possible_action_path = self.snapshot_result_path.joinpath("s_possible_action.jsonl")
        self.s_action_path = self.snapshot_result_path.joinpath("s_action.jsonl")
        # self.s_action_screenshot = self.mode_path_map['s_exp'].joinpath("all_actions.png")

    def initiate(self, recreate: bool = False):
        if not recreate:
            if self.initiated_path.exists():
                with open(self.initiated_path) as f:
                    content = f.read()
                if "STRUCTURE" in content:
                    return
        if self.snapshot_result_path.exists():
            shutil.rmtree(self.snapshot_result_path.absolute())
        self.snapshot_result_path.mkdir()
        # ------- Old -----
        self.ovsersight_path.mkdir()
        for path in self.mode_path_map.values():
            path.mkdir()
        self.action_path.touch()
        self.visited_elements_path.touch()
        self.s_action_path.touch()
        # ------- End Old -----
        with open(self.initiated_path, "w") as f:
            f.write("STRUCTURE\n")

    def initiate_talkback_explore_$$(self):
        if self.audit_path_map[AddressBook.TALKBACK_EXPLORE].exists():
            shutil.rmtree(self.audit_path_map[AddressBook.TALKBACK_EXPLORE].resolve())
        self.audit_path_map[AddressBook.TALKBACK_EXPLORE].mkdir()

    def initiate_extract_actions_$$(self):
        if self.audit_path_map[AddressBook.EXTRACT_ACTIONS].exists():
            shutil.rmtree(self.audit_path_map[AddressBook.EXTRACT_ACTIONS].resolve())
        self.audit_path_map[AddressBook.EXTRACT_ACTIONS].mkdir()

    def initiate_perform_actions_$$(self):
        if self.audit_path_map[AddressBook.PERFORM_ACTIONS].exists():
            shutil.rmtree(self.audit_path_map[AddressBook.PERFORM_ACTIONS].resolve())
        self.audit_path_map[AddressBook.PERFORM_ACTIONS].mkdir()
        self.perform_actions_results_path.touch()
        modes = ["tb_touch", "touch", "a11y_api"]
        for mode in modes:
            path = self.mode_path_map[mode]
            if path.exists():
                shutil.rmtree(path.resolve())
            path.mkdir()


    def initiate_process_screenshot_$$(self):
        if self.audit_path_map[AddressBook.PROCESS_SCREENSHOT].exists():
            shutil.rmtree(self.audit_path_map[AddressBook.PROCESS_SCREENSHOT].resolve())
        self.audit_path_map[AddressBook.PROCESS_SCREENSHOT].mkdir()

    def result_path(self) -> str:
        return self.snapshot_result_path.parent.parent.name

    def get_bm_log_path(self, extension: str = "") -> Path:
        log_name = self.snapshot_name()
        if extension:
            log_name += "_" + extension
        return self.snapshot_result_path.parent.joinpath(log_name + ".log")

    def app_name(self) -> str:
        return self.snapshot_result_path.parent.name

    def package_name(self) -> str:
        return self.app_name().split('(')[0]

    def snapshot_name(self) -> str:
        return self.snapshot_result_path.name

    def get_screenshot_path(self, mode: str, index: Union[int, str], extension: str = None,
                            should_exists: bool = False):
        file_name = f"{index}_{extension}.png" if extension else f"{index}.png"
        if not extension and mode == 's_exp':
            file_name = "INITIAL.png"
        return self._get_path(mode, file_name, should_exists)

    def get_gif_path(self, mode: str, index: Union[int, str], extension: str = None,
                            should_exists: bool = False):
        file_name = f"{index}_{extension}.gif" if extension else f"{index}.gif"
        if not extension and mode == 's_exp':
            file_name = "INITIAL.png"
        return self._get_path(mode, file_name, should_exists)

    def get_layout_path(self, mode: str, index: int, should_exists: bool = False):
        if mode == 's_exp' or mode == AddressBook.BASE_MODE:
            index = 'INITIAL'
        return self._get_path(mode, f"{index}.xml", should_exists)

    def get_log_path(self, mode: str, index: int, extension: str = None, should_exists: bool = False):
        file_name = f"{index}_{extension}.log" if (
                extension is not None and extension != ---_%%%_TAG) else f"{index}.log"
        return self._get_path(mode, file_name, should_exists)

    def get_instrumented_log_path(self, mode: str, index: int, should_exists: bool = False):
        file_name = f"{index}_instrumented.log"
        return self._get_path(mode, file_name, should_exists)

    def get_activity_name_path(self, mode: str, index: int, should_exists: bool = False):
        return self._get_path(mode, f"{index}_activity_name.txt", should_exists)
