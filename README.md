## os-autoinst-distri-kdelinux
> End-to-end tests for KDE Linux using [openQA](https://open.qa/).

### What's tested

#### Install test suite (`install-system`)

| Test | What it does |
|---|---|
| `kdelinux-live/bootup` | Powers on, checks UEFI screen, Plymouth, and live desktop loads |
| `common/system_settings/disable_screen_dim_and_screen_off` | Disables screen dim/off via kconfig so subsequent tests aren't interrupted |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
| `common/network` | Checks that networking works; a non-loopback link is up with a routable IP and a default route, DNS resolves, and HTTPS to the internet works |
| `kdelinux-live/calamares_install` | Runs the Calamares installer and installs the system, fatal |
| `kdelinux-live/bootup_setup` | Powers on after install, checks Plymouth and Plasma Welcome screen appear |
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
| `kdelinux/desktop/drkonqi` | Crashes an application and checks that DrKonqi produces a useful crash report. |
| `kdelinux/app/dolphin` | Does a smoke test for file management in Dolphin by creating a file, moving it to trash, then emptying trash. |
| `kdelinux/app/firefox` | Launches Firefox and checks that the Plasma Integration extension is active. |
| `kdelinux/app/package_compatibility_helper` | Checks the Package Compatibility Helper opens for an unsupported package type. |
| `kdelinux/app/discover_install` | Installs, launches, and uninstalls an application through Discover. |
| `kdelinux/desktop/desktop_session_services` | Checks whether any essential process has ever crashed. Every crash that dumps core is recorded by systemd-coredump, so we ask coredumpctl and fail if any of the processes we care about show up. This test should be run at the very *end* of the test suite. |
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
- FDE and manual partitioning - test installation with these
  - This will need some scheduler changes. We need to add a setting to main.pm for INSTALL_TYPE, which can be default|fde|manual
  - Then we need distinct named test-suites - install-system\[-fde|-manual\]
  - Then do some fancy combinatorics in CI, use matrices. This is because we don't do things the "normal" OpenQA way with persistent hosted runners (our way is better!).
  - The caveat with this is we'd be downloading an image many times. We should have some kind of cache for this or shared volume.
- Ensure a new build can upgrade to an even newer one - see https://invent.kde.org/kde-linux/os-autoinst-distri-kdelinux/-/work_items/11. This is going to be weird to implement.

### End-to-end test flows

Two flows are run against each build:

The standard flow, which verifies the current build installs and runs correctly:
```
install-system -> sanity-test
```

The upgrade flow, verifies the current build can be upgraded to from the previous build:
```
install-system (previous build) -> upgrade-system -> sanity-test
```

### Running tests locally

Nota bene: if you change anything in `extensions/`, you'll need to rerun your local worker/single-instance image so it can create a new sysext.

#### Full local stack (worker + webui)

Spins up a local OpenQA webui and worker together.

1. Place a KDE Linux `.iso` image in the repo root (the worker finds it automatically). Otherwise, it will try to download the latest one.
2. Start the stack:
   ```bash
   ./mock.sh up
   ```
3. The web UI is available at http://localhost:1080 once the container is ready. The container sets
   up the worker and test assets but does not submit jobs automatically. You must do this yourself.
4. Open a shell in the container and submit jobs:
   ```bash
   podman exec -it openqa-single-instance bash
   bash utils/jobs.sh            # add --upgrade for the upgrade flow
   ```
   You can also edit `utils/jobs.sh` to comment out jobs and run only the ones you want. Note that
   `sanity-test` needs `install-system` to have run first, because it installs the system to a virtual disk.
5. Tear down when done (this cleans up volumes):
   ```bash
   ./mock.sh down -v
   ```

`mock.sh` passes any additional arguments to `podman-compose`, so `./mock.sh up -d` etc. all work.

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

This assumes you're running KDE Linux, which will have `selenium-webdriver-at-spi` installed.

Inside the repository, go into the sysext test directory:
```
cd ./extensions/openqa/usr/lib/kde-linux-openqa
```

Then, create a venv and download test dependencies:
```
python3 -m venv --system-site-packages --upgrade-deps ./venv
source ./venv/bin/activate
pip3 install -r ./requirements.txt
```

As root, create required directories that the tests will output files to:
```
mkdir -p /var/log/kde-linux-openqa
chmod 777 /var/log/kde-linux-openqa
```

Then, run your test:
```
PYTHONPATH=. TEST_WITH_CLEAN_HOME=0 TEST_WITH_VIDEO_RECORDER=0 \
  KWIN_PID=$(pgrep -n kwin_wayland) \
  selenium-webdriver-at-spi-run python3 tests/<name of test>.py
```

### Integration with GitLab CI

The pipeline has three stages: `validate`, `test`, and `test-upgrade`.

| Stage | What it does |
|---|---|
| validate | runs [REUSE](https://reuse.software/) license compliance linting. This is skipped when the pipeline is triggered from another project. |
| test | runs the install + sanity-test suite (`worker.sh`) against the hosted openQA server. |
| test-upgrade | runs the upgrade suite (`worker.sh --upgrade`) against the hosted openQA server. |

Both test jobs use the upstream `openqa_worker` container image.

#### CI variables

The following variables must be configured in the GitLab project settings, and should be marked as `masked` and `protected`:

| Variable | What it's for |
|---|---|
| `OPENQA_API_KEY` | API key from the openQA web UI |
| `OPENQA_API_SECRET` | Corresponding API secret |

`OPENQA_HOST_ADDR` is hardcoded in `.gitlab-ci.yml` and does not need to be set as a variable.

#### Job groups

Each flow is assigned to its own job group so it gets a separate build overview and the dependency chain stays together. 
These groups should created on the server beforehand, under a `KDE Linux` folder:

| Group | Used by |
|---|---|
| `KDE Linux Installation` | standard install and sanity test flow |
| `KDE Linux Upgrade` | upgradeability flow |

The names are matched server-side by `utils/jobs.sh`. If a group doesn't exist, openQA will simply leave them ungrouped
without any errors.

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
