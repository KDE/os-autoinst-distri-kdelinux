# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType


class TestKind(StrEnum):
    OPENQA = "openqa"
    SELENIUM = "selenium"
    PYTHON = "python"


@dataclass(frozen=True)
class Test:
    path: Path
    kind: TestKind
    user: str | None = None
    timeout: int = 90
    artifacts: tuple[str, ...] = ()
    fatal: bool = False
    always_run: bool = False
    override: Path | None = None
    enabled: bool = True

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def source(self) -> Path:
        return Path("tests") / self.path


@dataclass(frozen=True)
class Suite:
    name: str
    action: SuiteAction
    # Can't use a dict here, test order and repeats are meaningful.
    tests: tuple[Test, ...]

    @property
    def enabled_tests(self) -> tuple[Test, ...]:
        return tuple(test for test in self.tests if test.enabled)


class SuiteAction(StrEnum):
    INSTALL = "install"
    UPGRADE = "upgrade"
    TEST = "test"


@dataclass(frozen=True)
class Flow:
    name: str
    suites: list[Suite]
    variables: list[str]


@dataclass(frozen=True)
class Manifest:
    """Representation of a tests.toml file and its declared test suites."""
    # All TOML-specific parsing and implementation should live in this class.

    manifest_path: Path
    name: str
    distri: str
    suites: Mapping[str, Suite]
    flows: Mapping[str, Flow]

    @classmethod  # factory method
    def load(cls, manifest_path: Path) -> Manifest:
        """
        Creates a Manifest object from a tests.toml manifest file.
        """
        manifest_path = manifest_path.expanduser().resolve()
        data = tomllib.loads(manifest_path.read_text())
        raw_suites = data.get("suites")
        raw_flows = data.get("flows")

        # Global state - this is the name of the OS being tested
        # and the contents of the DISTRI test variable.
        name = _validate_string(data, "name", f"Manifest {manifest_path}")
        distri = _validate_string(data, "distri", f"Manifest {manifest_path}")

        if not isinstance(raw_suites, dict):
            raise TypeError(f"Manifest {manifest_path} must define suites")

        if not isinstance(raw_flows, dict):
            raise TypeError(f"Manifest {manifest_path} must define flows")

        # Validate suites, then load.
        suites: dict[str, Suite] = {}
        for suite_name, settings in raw_suites.items():
            if not isinstance(suite_name, str):
                raise TypeError("Suite names must be strings")
            if not isinstance(settings, dict):
                raise TypeError(f"Suite {suite_name!r} must be a table")
            suites[suite_name] = _load_suite(
                manifest_path.parent,
                suite_name,
                settings,
            )

        # Validate flows, then load.
        flows: dict[str, Flow] = {}
        for flow_name, settings in raw_flows.items():
            if not isinstance(flow_name, str):
                raise TypeError("Flow names must be strings")
            if not isinstance(settings, dict):
                raise TypeError(f"Flow {flow_name!r} must be a table")
            flows[flow_name] = _load_flow(
                manifest_path.parent,
                flow_name,
                settings,
                suites
            )

        return cls(
            manifest_path=manifest_path,
            name=name,
            distri=distri,
            suites=MappingProxyType(suites),  # read-only view over a dict
            flows=MappingProxyType(flows),
        )

    @property
    def casedir(self) -> Path:
        """Return the repository root containing the manifest's tests directory."""
        return self.manifest_path.parent.parent

    def suite(self, name: str) -> Suite:
        try:
            return self.suites[name]
        except KeyError as error:
            raise ValueError(f"Unknown test suite {name!r}") from error

    def flow(self, name: str) -> Flow:
        try:
            return self.flows[name]
        except KeyError as error:
            raise ValueError(f"Unknown flow {name!r}") from error

    def all_tests(self) -> tuple[Test, ...]:
        return tuple(test for suite in self.suites.values() for test in suite.tests)


def _validate_string(
    data: dict[str, object],
    key: str,
    prefix: str
) -> str:
    """
    Return a field from a parsed manifest after validating.
    """
    value = data.get(key)

    if not isinstance(value, str):
        raise TypeError(f"{prefix} requires string {key!r}")
    if not value:
        raise ValueError(f"{prefix} requires non-empty {key!r}")
    return value


def _load_flow(
    source_dir: Path,
    name: str,
    settings: dict[str, object],
    suites: dict[str, Suite],
) -> Flow:
    """
    Parse a validated flow table into a typed Flow object.
    """
    raw_suites = settings.get("suites")
    variables = settings.get("variables", [])  # this is optional

    if not isinstance(raw_suites, list):
        raise TypeError(f"Flow {name!r} must define a suites array")

    if not isinstance(variables, list) or not all(
        isinstance(variable, str) for variable in variables
    ):
        raise TypeError(f"Flow {name!r} variables must be an array of strings")

    # Validate suite references, explode if one doesn't exist.
    resolved_suites: list[Suite] = []
    for suite_name in raw_suites:
        if not isinstance(suite_name, str):
            raise TypeError(f"Flow {name!r} suite names must be strings")

        if suite_name not in suites:
            raise ValueError(
                f"Flow {name!r} references unknown suite {suite_name!r}"
            )

        resolved_suites.append(suites[suite_name])

    return Flow(name=name, suites=resolved_suites, variables=variables)


def _load_suite(
    source_dir: Path,
    name: str,
    settings: dict[str, object],
) -> Suite:
    """
    Parse a validated suite table into a typed Suite object.
    """

    action = _validate_string(settings, "action", f"Suite {name!r}")

    raw_tests = settings.get("tests")
    if not isinstance(raw_tests, list):
        raise TypeError(f"Suite {name!r} must define a tests array")

    tests = tuple(_load_test(source_dir, raw_test) for raw_test in raw_tests)
    return Suite(name=name, action=SuiteAction(action), tests=tests)


def _load_test(source_dir: Path, raw_settings: object) -> Test:
    """
    Validate and convert a raw TOML test into a typed Test object.
    """
    # Ensure the TOML format is a typed dict.
    if not isinstance(raw_settings, dict):
        raise TypeError("Each manifest test must be a table")
    settings = raw_settings.copy()

    # Parse the test path.
    settings["path"] = _test_path(settings.get("path"))

    # Parse the test kind.
    raw_kind = settings.pop("type", None)
    try:
        settings["kind"] = TestKind(raw_kind)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Unsupported test type {raw_kind!r}") from error

    # Check and parse the override path.
    if settings.get("override") is not None:
        settings["override"] = _test_path(settings["override"])
    if "artifacts" in settings:
        artifacts = settings["artifacts"]
        if not isinstance(artifacts, list) or not all(
            isinstance(artifact, str) for artifact in artifacts
        ):
            raise ValueError("Test artifacts must be an array of strings")
        settings["artifacts"] = tuple(artifacts)

    # Pass parsed settings into Test ctor.
    try:
        test = Test(**settings)
    except TypeError as error:
        raise ValueError(f"Invalid test definition {raw_settings!r}") from error

    # Validate the outputted Test ctor.
    if test.kind is not TestKind.OPENQA and test.path.suffix != ".py":
        raise ValueError(f"SUT test must be Python: {test.path}")
    if test.user not in {None, "root", "live", "installed", "plasma_setup"}:
        raise ValueError(f"Unknown test user {test.user!r}")

    # Fail while loading rather than finding out that an implementation is missing
    # during sysext staging or, even worse, after an openQA job is submitted.
    for path in (test.path, test.override):
        if path is not None and not (source_dir / path).is_file():
            raise FileNotFoundError(source_dir / path)

    return test


def _test_path(value: object) -> Path:
    """
    Validate the path to a test.
    """
    if not isinstance(value, str):
        raise TypeError(f"Invalid test path {value!r}")

    path = Path(value)
    if (
        not re.fullmatch(r"[\w./-]+", value)
        or path.is_absolute()
        or ".." in path.parts
        or path.suffix not in {".py", ".pm"}
    ):
        raise ValueError(f"Invalid test path {value!r}")
    return path
