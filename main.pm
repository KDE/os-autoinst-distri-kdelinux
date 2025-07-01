use strict;
use warnings;

use testapi;
use File::Find;
use autotest;

sub loadtest {
    my ($path) = @_;
    my $filename = $path =~ /\.p[my]$/ ? $path : $path . '.pm';
    autotest::loadtest("tests/$filename");
}

sub test_live_image {
    loadtest 'kdelinux_live/boot_to_desktop.py';
    loadtest 'kdelinux_live/install_system/calamares_welcome.py';
    loadtest 'kdelinux_live/install_system/calamares_timezone.py';
    loadtest 'kdelinux_live/install_system/calamares_keyboard.py';
    loadtest 'kdelinux_live/install_system/calamares_partition.py';
    loadtest 'kdelinux_live/install_system/calamares_usersetting.py';
    loadtest 'kdelinux_live/install_system/calamares_install.py';
    loadtest 'kdelinux_live/shutdown.py';
}

sub test_kdelinux {
    loadtest 'kdelinux/boot_to_desktop/pre_login.py';
    loadtest 'kdelinux/boot_to_desktop/sddm_password_login.py';
}

if (get_var('DO_INSTALL', 0)) {
    test_live_image();
} else {
    test_kdelinux();
}

1;