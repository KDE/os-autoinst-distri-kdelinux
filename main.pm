use strict;
use warnings;

use testapi;
use File::Find;
use autotest;

use Inline::Python qw(py_eval);
use Cwd 'abs_path';
use File::Basename;

my $distri_path = dirname(abs_path(__FILE__));

py_eval("import sys; sys.path.insert(0, '$distri_path')");

sub loadtest {
    my ($path) = @_;
    my $filename = $path =~ /\.p[my]$/ ? $path : $path . '.pm';
    autotest::loadtest("tests/$filename");
}

sub test_live_image {
    loadtest 'common/bootup.py';
#    loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux-live/install_system/calamares_welcome.py';
    loadtest 'kdelinux-live/install_system/calamares_timezone.py';
    loadtest 'kdelinux-live/install_system/calamares_keyboard.py';
    loadtest 'kdelinux-live/install_system/calamares_partition.py';
    loadtest 'kdelinux-live/install_system/calamares_usersetting.py';
    loadtest 'kdelinux-live/install_system/calamares_install.py';
    loadtest 'common/shutdown.py';
}

sub test_kdelinux {
    loadtest 'common/bootup.py';
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
    loadtest 'common/shutdown.py';
}

sub test_system_upgrade {
    loadtest 'common/bootup.py';
#    loadtest 'kdelinux/desktop/kiss.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
    loadtest 'common/system_settings/disable_screen_lock.py';
    loadtest 'common/system_settings/disable_screen_dim_and_screen_off.py';
    loadtest 'kdelinux/app/upgrade_system.py';
    loadtest 'common/reboot.py';
    loadtest 'common/bootup.py';
    loadtest 'kdelinux/sddm/sddm_password_login.py';
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
