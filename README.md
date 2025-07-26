## os-autoinst-distri-kdelinux
> End-to-end tests for KDE Linux using [openQA](https://open.qa/).



### Tests





### Bootstrap and start running existing tests on your host

* Start the openQA environment (Terminal 1)
  ```bash
  git clone https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git
  cd os-autoinst-distri-kdelinux
  podman run --rm -it \
      -v "$PWD":/builds/1/project \
      -w /builds/1/project \
      -p 5991:5991 -p 1443:443 -p 5990:5990 -p 1080:80 -p 9526:9526 \
      --device /dev/kvm  \
      --name openqa-server \
      registry.opensuse.org/devel/openqa/containers/openqa-single-instance
  ```

* When you see the openQA worker is ready![image-20250725215212187](/home/anicaazhu/os-autoinst-distri-kdelinux/img/README/image-20250725215212187.png), Launch Another terminal and run trigger the test job.
  ```bash
  podman exec -it openqa-server bash
  ```
  ```bash
  ./utils/mocks/job_live+fullsystem/mock.sh --CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git
  ```



### Architecture



### Integrate with Gitlab CI

