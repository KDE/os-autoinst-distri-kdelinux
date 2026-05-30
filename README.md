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

### End-to-End testing scenarios
We offer 2 E2E testing scenarios.

1. Install the latest raw file, which contains the live system, from KDE storage. Boot the live system up, and use it to install the full system. After installation, boot up and sanity check this installed system.
2. Install the raw file produced by previously successful build (typically speaking yesterday's raw file, in contrast to today's), which contains the live system, from KDE storage. Boot this live system up, and use it to install the full system. After installation, boot up and sanity check this installed system. Then try to update the system from yesterday's build to today's build, and sanity check today's build.


### Integration with GitLab CI

The pipeline has three stages: `validate`, `test`, and `test-upgrade`.

- **validate** — runs [REUSE](https://reuse.software/) licence compliance linting. This is skipped when the pipeline is triggered from another project.
- **test** — runs the install + sanity-test suite (`worker.sh`) against the hosted openQA server.
- **test-upgrade** — runs the upgrade suite (`worker.sh --upgrade`) against the hosted openQA server.

Both test jobs use the upstream `openqa_worker` container image.

#### CI variables

The following variables must be configured in the GitLab project settings, and should be marked as `masked` and `protected`:

- `OPENQA_API_KEY` - API key from the openQA web UI
- `OPENQA_API_SECRET` - Corresponding API secret
- `OPENQA_SSH_PRIVATE_KEY` - Private key for sftp asset uploads to the openQA server (paste the key contents, not a file path)

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
