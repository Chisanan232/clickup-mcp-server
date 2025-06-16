#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Automate to deploy the latest version content of documentation.
#
# Description:
# It doesn't care about project version. It will use the latest version content to deploy in documentation.
#
# Allowable options:
#  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]
#  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]
#
#####################################################################################################################

Running_Mode="false"
#Running_Mode="dry-run"    # dry run for testing

sync_code() {
    # note: https://github.com/jimporter/mike?tab=readme-ov-file#deploying-via-ci
    git fetch origin gh-pages --depth=1
}

set_git_config() {
    git config --global user.name github-actions[bot]
    git config --global user.email chi10211201@cycu.org.tw
}

declare Latest_Version_Alias_Name="latest"

push_new_version_to_document_server() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "👨‍💻 This is debug mode, doesn't really deploy the new version to document."
        echo "👨‍💻 Under running command line: poetry run mike deploy --push $Latest_Version_Alias_Name"
    else
#        poetry run mike deploy --message "[bot] Deploy a new version documentation." --push --update-aliases "$New_Release_Version" latest
        poetry run mike deploy --push $Latest_Version_Alias_Name
    fi

    echo "🍻 Push new version documentation successfully!"
}

# The process what the shell script want to do truly start here
echo "👷  Start to push new version documentation ..."

sync_code
set_git_config
push_new_version_to_document_server

echo "👷  Deploy new version documentation successfully!"
