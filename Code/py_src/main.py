import sys
from pathlib import Path
import argparse
import asyncio
import logging
from typing import Union

from consts import &&&ICE_NAME, ADB_HOST, ADB_PORT
from ppadb.client_async import ClientAsync as AdbClient
from results_utils import AddressBook
from logger_utils import ColoredFormatter
from snapshot import EmulatorSnapshot, &&&iceSnapshot, Snapshot
from $$.app_$$ import TakeSnapshot$$, StoatSaveSnapshot$$
from $$.create_action_gif_$$ import CreateActionGif$$
from $$.execute_usecase_$$ import ExecuteUsecase$$
from $$.extract_actions_$$ import ExtractActions$$
from $$.perform_actions_$$ import PerformActions$$
from $$.process_screenshot_$$ import ProcessScreenshot$$
from $$.record_usecase_$$ import RecordUsecase$$
from $$.snapshot_$$ import RemoveSummary$$
from $$.talkback_explore_$$ import TalkBackExplore$$

logger = logging.getLogger(__name__)


async def execute_snapshot_$$(args, address_book: AddressBook):
    try:
        if not args.static:
            client = AdbClient(host=args.adb_host, port=args.adb_port)
            &&&ice = await client.&&&ice(args.&&&ice)
            if args.emulator:
                snapshot = EmulatorSnapshot(address_book=address_book,
                                            &&&ice=&&&ice,
                                            no_save_snapshot=args.no_save_snapshot)
                await snapshot.setup(first_setup=True, initial_emulator_load=args.initial_load)
            else:
                snapshot = &&&iceSnapshot(address_book=address_book, &&&ice=&&&ice)
                await snapshot.setup(first_setup=True)
        else:
            snapshot = Snapshot(address_book=address_book)
            await snapshot.setup()

        if args.snapshot_$$ == "talkback_explore":
            logger.info("Snapshot $$: TalkBack Explore")
            await TalkBackExplore$$(snapshot).execute()
        elif args.snapshot_$$ == "extract_actions":
            logger.info("Snapshot $$: Extract Actions")
            await ExtractActions$$(snapshot).execute()
        elif args.snapshot_$$ == "remove_summary":
            logger.info("Snapshot $$: Remove Summary")
            await RemoveSummary$$(snapshot).execute()
        elif args.snapshot_$$ == "perform_actions":
            logger.info("Snapshot $$: Perform Actions")
            await PerformActions$$(snapshot).execute()
        elif args.snapshot_$$ == "create_action_gif":
            logger.info("Snapshot $$: Create Action Gif")
            await CreateActionGif$$(snapshot).execute()
        elif args.snapshot_$$ == "process_screenshot":
            logger.info("Snapshot $$: Process Screenshot")
            await ProcessScreenshot$$(snapshot).execute()
    except Exception as e:
        logger.error("Exception happened in analyzing the snapshot", exc_info=e)


async def execute_app_$$(args, app_path: Path):
    try:
        if args.static:
            logger.error("Not supported")
            return

        client = AdbClient(host=args.adb_host, port=args.adb_port)
        &&&ice = await client.&&&ice(args.&&&ice)

        if args.app_$$ == "take_snapshot":
            logger.info("App $$: Take a snapshot")
            await TakeSnapshot$$(app_path=app_path, &&&ice=&&&ice).execute()
        elif args.app_$$ == "stoat_save_snapshot":
            logger.info("App $$: Save an Emulator Snapshot")
            if not args.emulator or args.no_save_snapshot:
                logger.error("The &&&ice should be an emulator")
                return
            await StoatSaveSnapshot$$(app_path=app_path, &&&ice=&&&ice).execute()

        elif args.app_$$ == "record_usecase":
            logger.info("App $$: Record a use case")
            await RecordUsecase$$(app_path=app_path, &&&ice=&&&ice).execute()
        elif args.app_$$ == "execute_usecase":
            logger.info("App $$: Execute a use case")
            await ExecuteUsecase$$(app_path=app_path, &&&ice=&&&ice).execute()

    except Exception as e:
        logger.error("Exception happened in analyzing the snapshot", exc_info=e)


def initialize_logger(log_path: Union[str, Path], quiet: bool = False, debug: bool = True):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger_handlers = [logging.FileHandler(log_path, mode='w')]
    logger_handlers[0].setFormatter(ColoredFormatter(detailed=True, use_color=True))
    if not quiet:
        logger_handlers.append(logging.StreamHandler())
        logger_handlers[-1].setFormatter(ColoredFormatter(detailed=False, use_color=True))
    logging.basicConfig(handlers=logger_handlers)
    # ---------------- Start Hack -----------
    py_src_path = Path(sys.argv[0]).parent
    py_src_file_names = [p.name[:-len(".py")] for p in py_src_path.rglob('*.py')]
    for name in logging.root.manager.loggerDict:
        if name.split('.')[-1] in py_src_file_names or name == "__main__":
            logging.getLogger(name).setLevel(level)
    # ----------------- End Hack ------------


if __name__ == "__main__":
    args = parser.parse_args()
    app_result_path = Path(args.output_path).joinpath(args.app_name)
    if args.snapshot_$$ is not None:
        snapshot_result_paths = []
        if args.snapshot:
            snapshot_result_paths = [app_result_path.joinpath(args.snapshot)]
            if not snapshot_result_paths[0].exists():
                snapshot_result_paths[0].mkdir(parents=True)
        else:
            for snapshot_result_path in app_result_path.iterdir():
                if snapshot_result_path.is_dir():
                    snapshot_result_paths.append(snapshot_result_path)

        if len(snapshot_result_paths) == 0:
            print("No snapshot is selected!")
            exit(1)
        for snapshot_result_path in snapshot_result_paths:
            snapshot_name = snapshot_result_path.name
            log_path_name = f"{snapshot_name}_{args.snapshot_$$}.log"
            log_path = app_result_path.joinpath(log_path_name)

            initialize_logger(log_path=log_path, quiet=args.quiet, debug=args.debug)
            logger.info(f"Executing {args.snapshot_$$} for Snapshot '{snapshot_name}' in app '{args.app_name}'...")
            address_book = AddressBook(snapshot_result_path)
            asyncio.run(execute_snapshot_$$(args=args, address_book=address_book))
            logger.info(f"Done executing {args.snapshot_$$} for Snapshot '{snapshot_name}' in app '{args.app_name}'")
    elif args.app_$$ is not None:
        if not app_result_path.exists() or not app_result_path.is_dir():
            app_result_path.mkdir()
        log_path = app_result_path.joinpath(f"app_{args.app_$$}.log")
        initialize_logger(log_path=log_path, quiet=args.quiet, debug=args.debug)
        logger.info(f"Executing {args.app_$$} for app '{args.app_name}'...")
        asyncio.run(execute_app_$$(args=args, app_path=app_result_path))
        logger.info(f"Done executing {args.app_$$}  in app '{args.app_name}'")
    else:
        print("Either app_$$ or snapshot_$$ should be provided!")
        exit(1)
