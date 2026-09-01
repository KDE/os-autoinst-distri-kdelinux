# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Philip Grant <pg_kde_invent@runbox.com>

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass

from dbus_fast import BusType
from dbus_fast.aio import MessageBus, ProxyInterface

BUS_NAME = "org.freedesktop.systemd1"
OBJECT_PATH = "/org/freedesktop/systemd1"
MANAGER_INTERFACE_NAME = "org.freedesktop.systemd1.Manager"


class SystemDBusInterfaceContext:
    def __init__(self) -> None:
        self.bus = MessageBus(bus_type=BusType.SYSTEM)

    async def __aenter__(self) -> ProxyInterface:
        await self.bus.connect()
        introspection = await self.bus.introspect(BUS_NAME, OBJECT_PATH)
        proxy = self.bus.get_proxy_object(BUS_NAME, OBJECT_PATH, introspection)
        return proxy.get_interface(MANAGER_INTERFACE_NAME)

    async def __aexit__(self, _exc_type, _exc, _tb) -> None:
        self.bus.disconnect()


@dataclass
class UnitState:
    """ Represents the state of a systemd unit, as returned by ListUnits()
    and related DBus methods of the "org.freedesktop.systemd1.Manager"
    interface. See
    https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.systemd1.html#Methods
    """
    unit_name: str
    unit_description: str
    load_state: str
    active_state: str
    sub_state: str
    followed_unit: str
    unit_object_path: str
    queued_job_id: int
    job_type: str
    job_object_path: str


class UnitStateFilter:
    def __init__(self,
                 attribute_name: str,
                 values: Iterable[str]) -> None:
        if attribute_name not in ("load_state", "active_state", "sub_state"):
            raise ValueError(f"Unexpected attribute for filtering: {attribute_name}")
        self.attribute_name = attribute_name
        if isinstance(values, str):
            # Treat as a single value, not an iterable of characters
            self.values = frozenset((values,))
        else:
            self.values = frozenset(values)

    def matches(self, state: UnitState) -> bool:
        return getattr(state, self.attribute_name) in self.values


async def get_unit_states(unit_names: Iterable[str],
                          interface: ProxyInterface) -> dict[str, UnitState]:
    state_arrays = await interface.call_list_units_by_names(unit_names)
    states_dict = {}
    for sa in state_arrays:
        state = UnitState(*sa)
        states_dict[state.unit_name] = state
    return states_dict


async def _wait_for_unit_state(unit_name: str,
                               attribute_name: str,
                               attribute_values: Iterable[str],
                               target_match_state: bool,
                               polling_interval_sec: float = 5.) -> None:
    state_filter = UnitStateFilter(attribute_name, attribute_values)
    async with SystemDBusInterfaceContext() as interface:
        while True:
            states = await get_unit_states([unit_name], interface)
            if state_filter.matches(states[unit_name]) == target_match_state:
                return
            await asyncio.sleep(polling_interval_sec)


async def wait_until_unit_state(unit_name: str,
                                attribute_name: str,
                                attribute_values: Iterable[str],
                                polling_interval_sec: float = 5.) -> None:
    """ Waits until <unit_name> reaches the given state: i.e. the given systemd
    <attribute_name> - which is one of "load_state", "active_state" or
    "sub_state" - has one of the values in <attribute_values>.
    """
    await _wait_for_unit_state(unit_name,
                               attribute_name,
                               attribute_values,
                               True,
                               polling_interval_sec=polling_interval_sec)


async def wait_while_unit_state(unit_name: str,
                                attribute_name: str,
                                attribute_values: Iterable[str],
                                polling_interval_sec: float = 5.) -> None:
    """ Waits until <unit_name> leaves the given state: i.e. the given systemd
    <attribute_name> - which is one of "load_state", "active_state" or
    "sub_state" - no longer has one of the values in <attribute_values>.
    """
    await _wait_for_unit_state(unit_name,
                               attribute_name,
                               attribute_values,
                               False,
                               polling_interval_sec=polling_interval_sec)
