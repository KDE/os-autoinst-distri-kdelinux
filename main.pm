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
    loadtest 'common/bootup.py';
    loadtest 'sut/bootstrap.py';
    loadtest 'sut/basic_test.py';
#    loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux-live/install_system/calamares_welcome.py';
#    loadtest 'kdelinux-live/install_system/calamares_timezone.py';
#    loadtest 'kdelinux-live/install_system/calamares_keyboard.py';
    loadtest 'kdelinux-live/install_system/calamares_partition.py';
#    loadtest 'kdelinux-live/install_system/calamares_usersetting.py';
    loadtest 'kdelinux-live/install_system/calamares_install.py';
#    loadtest 'common/shutdown.py';
    loadtest 'sut/shutdown.py';
}

sub test_kdelinux {
    loadtest 'common/bootup.py';
    loadtest 'sut/bootstrap.py';
    loadtest 'sut/basic_test.py';
#    loadtest 'kdelinux/desktop/kiss.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
    loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux/system_settings/configure_automatic_login.py';
    loadtest 'common/reboot.py';
    loadtest 'common/bootup.py';
    loadtest 'kdelinux/panel/system_tray.py';
    loadtest 'kdelinux/panel/digital_clock.py';
    loadtest 'kdelinux/desktop/create_file.py';
    loadtest 'kdelinux/desktop/switch_windows.py';
#    loadtest 'common/shutdown.py';
    loadtest 'sut/shutdown.py';
}

sub test_system_upgrade {
    loadtest 'common/bootup.py';
    loadtest 'sut/bootstrap.py';
    loadtest 'sut/basic_test.py';
#    loadtest 'kdelinux/desktop/kiss.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
    loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux/app/upgrade_system.py';
    loadtest 'common/reboot.py';
    loadtest 'common/bootup.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
#    loadtest 'common/shutdown.py';
    loadtest 'sut/shutdown.py';
}

if (get_var('DO_INSTALL', 0)) {
    test_live_image();
} elsif (get_var('DO_UPGRADE', 0)) {
    test_system_upgrade();
} else {
    test_kdelinux();
}

1;
