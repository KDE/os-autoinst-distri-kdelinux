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
- Panel tests - system tray popup, digital clock popup, create a file on the desktop, switch windows via the task manager, open an application from kickoff
- Desktop tests - create file on desktop, switch windows via task manager
- Firefox - basic browser functionality
- Discover app install - install a package via Discover
- Clipboard - Copy text in Firefox, paste into KWrite; Copy text in KWrite, paste into LibreOffice Calc; Copy a cell value in LibreOffice Calc, paste into Firefox address bar 

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
