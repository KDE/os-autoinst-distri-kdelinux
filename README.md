## os-autoinst-distri-kdelinux
> End-to-end tests for KDE Linux using [openQA](https://open.qa/).

### Development setup

The Python tooling requires Python 3.14 or newer and
[`uv`](https://docs.astral.sh/uv/). Install `uv`, then create and activate the
environment from the repository root:

```bash
uv sync
source .venv/bin/activate
```

The `qa worker` and `qa flow` commands run openQA jobs and are intended
to run inside mock containers or CI rather than on the host system.

See [Running tests locally](#running-tests-locally) for the mock and remote
openQA workflows. For these workflows, there is no need to install `uv` or
create the venv.

### What's tested

#### Install test suite (`install-system`)

| Test | What it does |
|---|---|
| `common/bootup` | Powers on, checks UEFI screen, Plymouth, and live desktop loads |
| `common/system_settings/disable_screen_dim_and_screen_off` | Disables screen dim/off via kconfig so subsequent tests aren't interrupted |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
| `common/network` | Checks that networking works; a non-loopback link is up with a routable IP and a default route, DNS resolves, and HTTPS to the internet works |
| `kdelinux-live/calamares_install` | Runs the Calamares installer and installs the system, fatal |
| `common/bootup` | Powers on after install, checks Plymouth and Plasma Welcome screen appear |
| `kdelinux/desktop/plasma_setup` | Completes the Plasma initial setup wizard |
| `kdelinux/sddm/sddm_password_login` | Types password at SDDM, checks desktop or welcome screen loads |
| `kdelinux/desktop/plasma_welcome` | Runs through the Plasma Welcome screen via Selenium |
| `kdelinux/system_settings/configure_automatic_login` | Configures automatic login via System Settings using Selenium |
| `common/shutdown` | Executes `systemctl poweroff` and waits for shutdown |

#### Sanity test suite (`sanity-test`)

| Test | What it does |
|---|---|
| `common/bootup` | Powers on; checks Plymouth and desktop panel (kickoff icon) load |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
| `common/network` | Checks that networking works; a non-loopback link is up with a routable IP and a default route, DNS resolves, and HTTPS to the internet works  |
| `kdelinux/system_settings/default_applications` | Verifies the set default applications, through mimetype and system settings. |
| `kdelinux/desktop/panel` | Checks if apps can be launched from Kickoff search, Kickoff favorites, and the task manager. Checks if the correct apps are pinned to task manager. Ensures that the system tray works and displays entries. |
| `kdelinux/desktop/task_switcher` | Checks that Alt+Tab task switcher moves focus between windows. The switcher is not on the a11y bus and is a part of KWin, so check the active state of KDialog windows. |
| `kdelinux/desktop/create_file` | Creates a new text file on the desktop and verifies it appears. |
| `kdelinux/desktop/clipboard` | Checks that text copies and pastes between an application and the system clipboard. |
| `kdelinux/desktop/krunner` | Searches for and launches an application through KRunner. |
| `kdelinux/desktop/secret_service` | Verifies the Secret Service provider is ksecretd and works through KeepSecret. |
| `kdelinux/desktop/vaults` | Creates an encrypted Plasma Vault through its system tray applet. |
| `kdelinux/desktop/drkonqi` | Crashes an application and checks that DrKonqi produces a useful crash report. |
| `kdelinux/app/dolphin` | Does a smoke test for file management in Dolphin by creating a file, moving it to trash, then emptying trash. |
| `kdelinux/app/firefox` | Launches Firefox and checks that the Plasma Integration extension is active. |
| `kdelinux/app/package_compatibility_helper` | Checks the Package Compatibility Helper opens for an unsupported package type. |
| `kdelinux/app/discover_install` | Installs, launches, and uninstalls an application through Discover. |
| `kdelinux/system/polkit_rules` | Checks that elevation still needs authentication; neither the installed user nor an account outside wheel is authorised for run0's polkit action before anyone has authenticated. |
| `kdelinux/system/system_development` | Toggles developer mode and runs set-up-system-development to install kde-builder, checking each works. |
| `kdelinux/system/snapper` | Checks the snapper setup for the per-user home subvolumes; the files it needs in `/etc`, the home template, the config created on login, snapshots taken by the user, and the config, snapshots and home going away with the user. |
| `kdelinux/system/collect_logs` | Runs collect-logs and checks it produces a redacted `.tar.zst` archive. |
| `kdelinux/system/desktop_session_services` | Checks whether any essential process has ever crashed. Every crash that dumps core is recorded by systemd-coredump, so we ask coredumpctl and fail if any of the processes we care about show up. This test should be run at the very *end* of the test suite. |
| `common/shutdown` | Executes `systemctl poweroff` and waits for shutdown |

#### Upgrade test suite (`upgrade-system`)

| Test | What it does |
|---|---|
| `common/bootup` | Powers on previous build; checks Plymouth and panel load |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
| `common/network` | Checks that networking works; a non-loopback link is up with a routable IP and a default route, DNS resolves, and HTTPS to the internet works, fatal |
| `kdelinux/app/discover_upgrade` | Upgrades the system via Discover, fatal |
| `common/reboot` | Executes `systemctl reboot` |
| `common/bootup` | Checks new build boots correctly after upgrade |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
| `common/shutdown` | Issues `systemctl poweroff` and waits for shutdown |

### TODO

- Bootability/upgradeability - UEFI boot menu shows both old and new system versions after an upgrade
- Lock screen - lock the session and unlock it with the user's password
- Clipboard - test outside of Qt apps and flatpaks (e.g. copy from Firefox, paste into LibreOffice Calc)
- Manual partitioning - add a Calamares installation flow and verify the resulting disk layout
- Ensure a new build can upgrade to an even newer one - see https://invent.kde.org/kde-linux/os-autoinst-distri-kdelinux/-/work_items/11. This is going to be weird to implement.

### Test layout

All tests live under `tests/`. `tests/tests.toml` declares the tests,
the distri name, test suites and test flows, 

Every `qa` command that works with tests accepts `--manifest-path <path>`, 
`--var <key>=<value>` and `--flavor-suffix=<value>`.
The manifest path defaults to `./tests/tests.toml`. Test paths in
`tests.toml` are relative to the directory containing `<path>`. 
Variables passed into `--var` are set as openQA test settings. For KDE Linux,
`FDE_INSTALL=1` is set through this mechanism. `--flavor-suffix` appends a
string to the end of the flavor value in the openQA webUI, and is used to
differentiate encryption runs.

#### Test suites

For KDE Linux, suites are grouped into `install-system`, `upgrade-system`,
and `sanity-test` suites.

```toml
name = "KDE Linux"
distri = "KDE-Linux"

[suites.example]
action = "install"
tests = [
    { path = "common/bootup.py", type = "openqa" },
    { path = "common/basic_test.py", type = "python" },
    { path = "kdelinux/app/firefox.py", type = "selenium", user = "installed", timeout = 180 },
]
```

`openqa` tests run on the host. `selenium` and `python` tests run inside the
SUT, with and without the Selenium runner respectively. Tests run in the
order that they are listed in, including repeats. `enabled = false` keeps a
test declared despite stopping it from being included in the schedule.

`action` describes disk interaction. Three options are accepted - `install`, 
`upgrade`, and `test`.

- `install`
  Boots the selected live image, sets the live-install flavor, and creates the installed HDD. Usually the first suite in an
  install flow.

- `upgrade`
  Boots from the already-installed HDD and sets DO_UPGRADE as an openQA test setting. It upgrades that installation using the selected update source.

- `test`
  Boots the existing installed HDD without installation or upgrade flags. This is for post-install or post-upgrade validation.

Before each job, the worker creates a temporary CASEDIR containing only the
selected tests - the original openQA tests and generated `CliTest`
wrappers that call SUT tests. It generates a minimal `main.pm` that calls
`autotest::loadtest` in manifest order, using the user, timeout, flags, and
artifacts previously declared for each SUT test. An explicit `override` path
can be used to select a custom wrapper instead,
with these also living under `tests/` beside their SUT script.
All paths in `tests.toml` are relative to `tests/`.

#### Test flows

Suites are run in the order defined in a test flow. For KDE Linux, flows are
grouped into `install` and `upgrade` flows.

The `install` flow, which verifies the current build installs and runs correctly:
```
install-system -> sanity-test
```

The `upgrade` flow, verifies the current build can be upgraded to from the previous build:
```
install-system (previous build) -> upgrade-system -> sanity-test
```

Both flows are run under each build. Flows are defined as per the below example:

```toml
[flows.install]
suites = ["install-system", "sanity-test"]
variables = ["FDE_INSTALL"]

[flows.upgrade]
suites = ["install-system", "upgrade-system", "sanity-test"]
variables = ["FDE_INSTALL"]
```

### Running tests locally

To rebuild the sysext without restarting the worker, enter the worker container:

```
./qa-mock enter
```

Then run:

```
./qa build-sysext
```

#### Full local stack (worker + webui)

Spins up a local OpenQA webui and worker together.

1. Place a KDE Linux `.iso` image in the repo root (the worker finds it automatically). Otherwise, it will try to download the latest one.
2. Start the stack. To test upgrading between local builds, mount a mkosi.output directory too:
   ```bash
   KDE_LINUX_OUTPUT=~/Projects/kde-linux/mkosi.output ./qa-mock up
   ```
3. The web UI is available at http://localhost:1080 once the container is ready. The container sets
   up the worker and test assets but does not submit jobs automatically. You must do this yourself.
4. Open a shell in the container and submit jobs:
   ```bash
   ./qa-mock enter
   ./qa flow install
   # For an encrypted install, add:
   #   --var FDE_INSTALL=1 --flavor-suffix=-encrypted
   ```
   To test an upgrade from a local ISO to a local build, pass the base ISO and
   the mounted `mkosi.output` directory:
   ```bash
   ./qa flow upgrade \
     --upgrade-from /casedir/kde-linux_202608010001.iso \
     --upgrade-to /kde-linux-output
   ```
   The newest complete build in that directory is exposed to the VM as a
   temporary sysupdate source. It must be newer than the base ISO.

   You can also run `./qa job` to run a specific job (use `./qa job --help` to see its options). Note that
   `sanity-test` needs `install-system` to have run first, because it installs the system to a virtual disk.
5. Tear down when done (this cleans up volumes):
   ```bash
   ./qa-mock down -v
   ```

`./qa-mock` passes any additional arguments to `podman-compose`, so `./qa-mock up -d` etc. all work.

#### SSH into the SUT

`./qa build-sysext` generates a temporary keypair for SSH authentication. The 
private key stays on the machine running the worker while the public key is put
into the sysext and is installed for all users. SSH password, keyboard-interactive, 
and challenge-response authentication are disabled, so public-key authentication is 
required to SSH into the SUT.

In the mock setup, the private key is inside the container at
`/tmp/kde-linux-openqa-root-key`. Run `ssh` inside the container:

```bash
podman exec -it openqa-single-instance ssh \
  -i /tmp/kde-linux-openqa-root-key -p 2222 root@127.0.0.1

# The same key works for any and every account
podman exec -it openqa-single-instance ssh \
  -i /tmp/kde-linux-openqa-root-key -p 2222 user@127.0.0.1
```

Otherwise, if `./qa build-sysext` was run locally, run:

```bash
ssh -i /tmp/kde-linux-openqa-root-key -p 2222 user@127.0.0.1
```

The key is generated when `build-sysext` runs and is installed in the SUT when
it boots up.

#### Running the worker against a remote OpenQA server

To run only the worker locally while pointing it at an existing hosted OpenQA instance, create a `.env` file in the repo root, based on `.env.example`:

```ini
OPENQA_HOST_ADDR=openqa.example.com
OPENQA_API_KEY=<your key>
OPENQA_API_SECRET=<your secret>
OPENQA_SCHEME=https
```

The API key and secret can be set up in the OpenQA web UI. 
You'll need operator or admin permissions on the server, and once you have these, you can generate an API key and secret through the user menu on the top right. Don't commit these!

Then run the worker via Podman:

```bash
podman-compose -f mocks/worker.yml up
```

The worker will register with the remote server, submit jobs, and stream results back. It is a single worker that triggers and consumes every test asset itself, so nothing is uploaded to the server.

#### Running a SUT Python `unittest` on your own machine

This assumes you're running KDE Linux, which will have
`selenium-webdriver-at-spi` installed.

From the repository root, create a venv and install the SUT dependency group:

```bash
python3 -m venv --system-site-packages --upgrade-deps ./venv
uv pip install --python ./venv/bin/python --group sut
source ./venv/bin/activate
```

As root, create the directory where the tests write their results:

```bash
mkdir -p /var/log/kde-linux-openqa
chmod 777 /var/log/kde-linux-openqa
```

Then run the desired test:

```bash
PYTHONPATH=. TEST_WITH_CLEAN_HOME=0 TEST_WITH_VIDEO_RECORDER=0 \
  KWIN_PID=$(pgrep -n kwin_wayland) \
  selenium-webdriver-at-spi-run python3 tests/<path>/<name>.py
```

### Integration with GitLab CI

The pipeline has three stages: `validate`, `test`, and `test-upgrade`.

| Stage | What it does |
|---|---|
| validate | runs [REUSE](https://reuse.software/) license compliance linting. This is skipped when the pipeline is triggered from another project. |
| test | runs plain and FDE install + sanity-test flows as a parallel matrix against the hosted openQA server. |
| test-upgrade | runs plain and FDE upgrade flows as a parallel matrix against the hosted openQA server. |

The test jobs use the upstream `openqa_worker` container image.

#### CI variables

The following variables must be configured in the GitLab project settings, and should be marked as `masked` and `protected`:

| Variable | What it's for |
|---|---|
| `OPENQA_API_KEY` | API key from the openQA web UI |
| `OPENQA_API_SECRET` | Corresponding API secret |

`OPENQA_HOST_ADDR` is hardcoded in `.gitlab-ci.yml` and does not need to be set as a variable.

#### Job groups

Each flow is assigned to its own job group so it gets a separate build overview and the dependency chain stays together. 
These groups should be created on the server beforehand, under a folder named
after the manifest's `name` value:

| Group | Used by |
|---|---|
| `<name> Installation` | standard install and sanity test flow |
| `<name> Upgrade` | upgradeability flow |

The names are derived from `name` in `tests/tests.toml`. If a group doesn't
exist, openQA will simply leave jobs ungrouped without any errors.

#### Triggering from another project

The pipeline is designed to be triggered from the [kde-linux](https://invent.kde.org/kde-linux/kde-linux) CI after a successful image build. When triggered this way, the REUSE lint job is skipped and both test jobs run automatically.

This works through a trigger job in KDE Linux's `.gitlab-ci.yml`:

```yaml
trigger-openqa:
  stage: test
  trigger:
    project: kde-linux/os-autoinst-distri-kdelinux
    branch: master
    strategy: depend
```

#### Running manually on a merge request

Test jobs have `when: manual` for merge request pipelines, so they won't consume runner resources automatically. They are to be triggered manually when you need to validate a change against the live openQA server.
