# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>
use strict;
use warnings;

use Inline::Python qw(py_eval);
use Cwd 'abs_path';
use File::Basename;

use lib 'lib';
my $distri_path = dirname(abs_path(__FILE__));
py_eval("import sys; sys.path.insert(0, '$distri_path')");

use testapi;
use File::Find;
use autotest;

$testapi::distri->add_console('virtio-terminal', 'virtio-terminal', { persistent => 1 });
$testapi::distri->add_console('desktop', 'vnc-base', { display => 0, hostname => 'localhost', port => 5991 });

sub loadtest {
    my ($path) = @_;
    my $filename = $path =~ /\.p[my]$/ ? $path : $path . '.pm';
    autotest::loadtest("tests/$filename");
}

sub test_live_image {
    loadtest 'kdelinux-live/bootup.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'common/basic_test.py';
    loadtest 'kdelinux-live/calamares_install.py';
    loadtest 'common/reboot.py';
    loadtest 'kdelinux-live/bootup_setup.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux/desktop/plasma_setup.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
    loadtest 'kdelinux/desktop/plasma_welcome.py';
    # loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'kdelinux/system_settings/configure_automatic_login.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'common/shutdown.py';
}

sub test_kdelinux {
    loadtest 'common/bootup.py';
    loadtest 'common/basic_test.py';
    # TODO unimplemented stubs
    # loadtest 'kdelinux/desktop/kickoff.py';
    # loadtest 'kdelinux/desktop/krunner.py';
    # loadtest 'kdelinux/desktop/system_tray.py';
    # loadtest 'kdelinux/desktop/task_manager.py';
    # loadtest 'kdelinux/desktop/task_switcher.py';
    # loadtest 'kdelinux/desktop/create_file.py';
    loadtest 'kdelinux/app/dolphin_manipulate_fs.py';
    loadtest 'kdelinux/desktop/drkonqi.py';
    loadtest 'kdelinux/app/firefox.py';
    loadtest 'kdelinux/app/clipboard.py';
    loadtest 'kdelinux/app/ensure_secret_service_provider.py';
    loadtest 'kdelinux/app/package_compatibility_helper.py';
    loadtest 'kdelinux/system_settings/check_default_applications.py';
    loadtest 'common/shutdown.py';
}

sub test_system_upgrade {
    loadtest 'common/bootup.py';
    loadtest 'common/basic_test.py';
    loadtest 'kdelinux/app/discover_upgrade.py';
    loadtest 'common/reboot.py';
    loadtest 'common/bootup.py';
    loadtest 'common/basic_test.py';
    loadtest 'common/shutdown.py';
}

if (get_var('DO_INSTALL', 0)) {
    test_live_image();
} elsif (get_var('DO_UPGRADE', 0)) {
    test_system_upgrade();
} else {
    test_kdelinux();
}

1;
