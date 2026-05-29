## os-autoinst-distri-kdelinux
> End-to-end tests for KDE Linux using [openQA](https://open.qa/).

### Test Coverage

| Feature Category | Test Case | Status |
|------------------|-----------|--------|
| [Ensure upgrading works](https://invent.kde.org/kde-linux/kde-linux/-/work_items/206) | Discover update page | ✅      |
| [Ensure basic desktop functionality works](https://invent.kde.org/kde-linux/kde-linux/-/work_items/178) | Create a text file on desktop | ✅      |
|  | Open system tray popup | ✅      |
|  | Open Digital Clock popup | ✅      |
|  | Switch windows using Task Manager | ✅      |
| [Ensure automatic login works](https://invent.kde.org/kde-linux/kde-linux/-/work_items/176) | Configure automatic login via System Settings | ✅      |
| [Ensure manual login works](https://invent.kde.org/kde-linux/kde-linux/-/work_items/175) | SDDM login | ✅      |
|  | TTY login / reboot / shutdown | ✅      |
| [Ensure bootability](https://invent.kde.org/kde-linux/kde-linux/-/work_items/174) | UEFI boot menu | ✅      |
|  | Plymouth boot splash | ✅      |
|  | Desktop panel loads | ✅      |
| | UEFI boot menu shows multiple system versions after upgrade | ✅      |
| [Ensure Firefox works]() | Test by can search google | TODO   |
| [Ensure installation from Discover works]() | Test by install steam | TODO   |



### Running tests locally

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

### Test Case Architecture(Todo: Guide)

### End-to-End testing scenarios
We offer 2 E2E testing scenarios.

1. Install the lastest raw file, which contains the live system, from KDE storage. Boot the live system up, and use it to install the full(complete) system. After installation, boot up and sanity check this installed system.
2. Install the raw file produced by previously successful build(typically speaking a yesterday's raw file, in contrast to today's), which contains the live system, from KDE storage. Boot this live system up, and use it to install the full(complete) system. After installation, boot up and sanity check this installed system. Then try to update the system from yesterday's build to today's build.


### Integrate with Gitlab CI

Currently, we offer two options for running CI jobs:

1. **An openQA instance** – an all-in-one, openSUSE-based image that includes the Web UI, a PostgreSQL database for storing test/job results and authentication/authorization data, the `openqa-worker` service, nginx, etc,.
2. **A lightweight backend-only image** – Also an openSUSE-based image, but contains only the test execution engine (`isotovideo`).

### How to Mock test running locally(Todo: Guide)

### Imperfections

1. **Mock script redundancy** - The current mock scripts (`utils/mocks/`) contain significant code duplication across different job types (live+fullsystem, live+upgrade). The scripts lack reusability and should be refactored to use shared components or a common base script with configurable parameters.

2. **TTY session implementation issues** - The implementation or even the existence of TTY session in `lib/sessions/syscore/tty.py` may have reliability problems, as I never used them.

3. **Desktop file creation test verification** - The desktop file creation test (`tests/kdelinux/desktop/create_file.py`) currently only verifies the file creation through the GUI. It should be enhanced to confirm that the file actually exists on the filesystem by checking via konsole or TTY session using serial output.

### Notes
- needles directory needs permissions 755 for the WebUI needle editor to work.

