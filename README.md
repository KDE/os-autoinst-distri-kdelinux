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



### Bootstrap and start running existing tests on your host

* Start the openQA environment (Terminal 1)
  ```bash
  git clone https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git
  cd os-autoinst-distri-kdelinux
  podman run --rm -it \
      -v "$PWD":/builds/1/project \
      -w /builds/1/project \
      -p 5991:5991 -p 1443:443 -p 5990:5990 -p 1080:80 -p 9526:9526 \
      --device /dev/kvm  \
      --name openqa-server \
      registry.opensuse.org/devel/openqa/containers/openqa-single-instance
  ```

* When you see the openQA worker is ready,![image-20250725215212187](./img/README/image-20250725215212187.png)

  Launch Another terminal and run codes below to trigger the test job.
  ```bash
  podman exec -it openqa-server bash
  ```
  ```bash
  ./utils/mocks/job_live+fullsystem/mock.sh --CASEDIR=/builds/1/project
  ```
* You can view the WebUI for the OpenQA at http://localhost:1080/

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

