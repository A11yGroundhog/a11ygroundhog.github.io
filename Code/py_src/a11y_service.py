import logging
import asyncio
from typing import List, Union
from adb_utils import run_bash
# TODO: Need to decompose $$_utils into $$_comms and $$_navigations
from $$_utils import is_$$_live
from consts import &&&ICE_NAME

logger = logging.getLogger(__name__)


class A11yServiceManager:
    services = {"tb": "com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService",
                         "$$": "&&&.XXXs.$$/&&&.XXXs.$$.app.My$$Service"}

    @staticmethod
    async def get_enabled_services(simplify: bool = False, &&&ice_name: str = &&&ICE_NAME) -> List[str]:
        _, enabled_services, _ = \
            await run_bash(f"adb -s {&&&ice_name} shell settings get secure enabled_accessibility_services")
        if 'null' in enabled_services:
            return []
        result = []
        for service in enabled_services.strip().split(':'):
            service_name = service
            if simplify:
                for key, value in A11yServiceManager.services.items():
                    if value == service_name:
                        service_name = key
                        break
            result.append(service_name)
        return result

    @staticmethod
    async def is_enabled(service_name: str, &&&ice_name: str = &&&ICE_NAME) -> bool:
        if service_name not in A11yServiceManager.services:
            return False
        enabled_services = await A11yServiceManager.get_enabled_services(&&&ice_name=&&&ice_name)
        return A11yServiceManager.services[service_name] in enabled_services

    @staticmethod
    async def enable(service_names: Union[str, List[str]], &&&ice_name: str = &&&ICE_NAME) -> int:
        if isinstance(service_names, str):
            service_names = [service_names]
        enabled_services = await A11yServiceManager.get_enabled_services(&&&ice_name=&&&ice_name)
        requested_services = []
        for service_name in service_names:
            if service_name not in A11yServiceManager.services:
                continue
            actual_service_name = A11yServiceManager.services[service_name]
            if actual_service_name in enabled_services:
                continue
            requested_services.append(actual_service_name)
        if len(requested_services) == 0:
            return 0

        enabled_services_str = ":".join(enabled_services + requested_services)
        r_code, *_ = await run_bash(
            f"adb -s {&&&ice_name} shell settings put secure enabled_accessibility_services {enabled_services_str}")
        return len(requested_services) if r_code == 0 else -1

    @staticmethod
    async def disable(service_name: str, &&&ice_name: str = &&&ICE_NAME) -> bool:
        if service_name not in A11yServiceManager.services:
            return False
        enabled_services = await A11yServiceManager.get_enabled_services(&&&ice_name=&&&ice_name)
        if A11yServiceManager.services[service_name] not in enabled_services:
            return True
        enabled_services.remove(A11yServiceManager.services[service_name])
        enabled_services_str = ":".join(enabled_services)
        if len(enabled_services_str) == 0:
            r_code, *_ = await run_bash(
                f"adb -s {&&&ice_name} shell settings delete secure enabled_accessibility_services")
        else:
            r_code, *_ = await run_bash(
                f"adb -s {&&&ice_name} shell settings put secure enabled_accessibility_services {enabled_services_str}")
        return r_code == 0

    @staticmethod
    async def setup_$$_a11y_services(tb=False, &&&ice_name: str = &&&ICE_NAME) -> None:
        requested_services = ["$$"]
        if tb:
            requested_services.append("tb")
        elif await A11yServiceManager.is_enabled("tb", &&&ice_name=&&&ice_name):
            logger.debug("Disabling TalkBack...")
            await A11yServiceManager.disable("tb", &&&ice_name=&&&ice_name)
            await asyncio.sleep(1)
        for i in range(3):
            enabled_count = await A11yServiceManager.enable(requested_services, &&&ice_name=&&&ice_name)
            if enabled_count > 0:
                logger.debug(f"{enabled_count} services are enabled from {requested_services}")
                await asyncio.sleep(1)
                break
            elif enabled_count == 0:
                break
            else:
                logger.warning(f"There was an issue with enabling services {requested_services}, Try: {i}")
        live_$$ = False
        for i in range(10):
            if await is_$$_live():
                live_$$ = True
                break
            else:
                logger.info(f"Waiting for $$ to be alive...")
        if not live_$$:
            # TODO: too harsh, it's better to return live_$$ and let the outer method decides
            raise "$$ is not alive"
