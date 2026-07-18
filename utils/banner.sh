# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

banner() {
    local level="$1" message="$2"
    local rule color out=1

    case "$level" in
        ERROR) rule='\e[1;91m'; color='\e[1;91m'; out=2 ;;
        WARN)  rule='\e[1;93m'; color='\e[1;93m'; out=2 ;;
        *)     rule='\e[1;95m'; color='\e[1;96m' ;;
    esac

    local line='━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    local message_line
    local prefix="[$level]"

    {
        printf '\n%b%s\e[0m\n' "$rule" "$line"

        while IFS= read -r message_line || [[ -n "$message_line" ]]; do
            printf '%-9s %b%s\e[0m\n' "$prefix" "$color" "$message_line"
            prefix=''
        done <<< "$message"

        printf '%b%s\e[0m\n\n' "$rule" "$line"
    } >&"$out"
}
