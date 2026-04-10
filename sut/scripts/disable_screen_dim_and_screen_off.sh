#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

kwriteconfig6 --file powerdevilrc --group "AC" --group "Display" --key "DimDisplayIdleTimeoutSec" "-1"
kwriteconfig6 --file powerdevilrc --group "AC" --group "Display" --key "DimDisplayWhenIdle" "false"
kwriteconfig6 --file powerdevilrc --group "AC" --group "SuspendAndShutdown" --key "AutoSuspendAction" "0"
