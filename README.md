## os-autoinst-distri-kdelinux
> End-to-end tests for KDE Linux using [openQA](https://open.qa/).

### What's tested

#### Install test suite (`install-system`)

| Test | What it does |
|---|---|
| `kdelinux-live/bootup` | Powers on, checks UEFI screen, Plymouth, and live desktop loads |
| `common/system_settings/disable_screen_dim_and_screen_off` | Disables screen dim/off via kconfig so subsequent tests aren't interrupted |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
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
| `kdelinux/system_settings/check_default_applications` | Verifies the set default applications, through mimetype and system settings. |
| `kdelinux/desktop/panel` | Checks if apps can be launched from Kickoff search, Kickoff favorites, and the task manager. Checks if the correct apps are pinned to task manager. Ensures that the system tray works and displays entries. |
| `kdelinux/desktop/task_switcher` | Checks that Alt+Tab task switcher moves focus between windows. The switcher is not on the a11y bus and is a part of KWin, so check the active state of KDialog windows. |
| `kdelinux/desktop/create_file` | Creates a new text file on the desktop and verifies it appears. |
| `kdelinux/desktop/clipboard` | Checks that text copies and pastes between an application and the system clipboard. |
| `kdelinux/desktop/krunner` | Searches for and launches an application through KRunner. |
| `kdelinux/desktop/drkonqi` | Crashes an application and checks that DrKonqi produces a useful crash report. |
| `kdelinux/app/dolphin_manipulate_fs` | Does a smoke test for file management in Dolphin by creating a file, moving it to trash, then emptying trash. |
| `kdelinux/app/firefox` | Launches Firefox and checks page loading and that the Plasma Integration extension is active. |
| `kdelinux/app/ensure_secret_service_provider` | Verifies the Secret Service provider is ksecretd and works through KeepSecret. |
| `kdelinux/app/package_compatibility_helper` | Checks the Package Compatibility Helper opens for an unsupported package type. |
| `kdelinux/app/discover_install` | Installs, launches, and uninstalls an application through Discover. |
| `kdelinux/desktop/desktop_session_services` | Checks whether any essential process has ever crashed. Every crash that dumps core is recorded by systemd-coredump, so we ask coredumpctl and fail if any of the processes we care about show up. This test should be run at the very *end* of the test suite. |
| `common/shutdown` | Executes `systemctl poweroff` and waits for shutdown |

#### Upgrade test suite (`upgrade-system`)

| Test | What it does |
|---|---|
| `common/bootup` | Powers on previous build; checks Plymouth and panel load |
| `common/basic_test` | Checks if the system is blessed and no services have failed |
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
- Ensure a new build can upgrade to an even newer one - see https://invent.kde.org/kde-linux/os-autoinst-distri-kdelinux/-/work_items/11

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

1. Place a KDE Linux `.raw` image in the repo root (the worker finds it automatically). Otherwise, it will try to download the latest one.
2. Start the stack:
   ```bash
   ./mock.sh up
   ```
3. The web UI is available at http://localhost:1080 once the container is ready. The worker connects automatically and submits jobs.
4. Tear down when done (this cleans up volumes):
   ```bash
   ./mock.sh down -v
   ```

`mock.sh` passes any additional arguments to `podman-compose`, so `./mock.sh up -d` etc. all work.

#### Running the worker against a remote OpenQA server

To run only the worker locally while pointing it at an existing hosted OpenQA instance, create a `.env` file in the repo root, based on `.env.example`:

```ini
OPENQA_HOST_ADDR=openqa.example.com
OPENQA_SSH_USER=openqa_server_user
OPENQA_API_KEY=<your key>
OPENQA_API_SECRET=<your secret>
OPENQA_SCHEME=https
OPENQA_SSH_PRIVATE_KEY=<your private key, NOT the path to the file>
```
`OPENQA_SSH_USER` must be the user running the OpenQA server, so assets can be sftp'd into the server.
You'll also need to have a SSH key pair, and have uploaded your public key to the server.

The API key and secret can be set up in the OpenQA web UI. 
You'll need operator or admin permissions on the server, and once you have these, you can generate an API key and secret through the user menu on the top right. Don't commit these!

Then run the worker via Podman:

```bash
podman-compose -f mocks/worker.yml up
```

The worker will register with the remote server, upload assets via SSH/sftp, submit jobs, and stream results back.

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
| `OPENQA_SSH_PRIVATE_KEY` | Private key for sftp asset uploads to the openQA server (paste the key contents, not a file path) |

`OPENQA_HOST_ADDR` and `OPENQA_SSH_USER` are hardcoded in `.gitlab-ci.yml` and do not need to be set as variables.

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
