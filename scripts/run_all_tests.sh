#!/usr/bin/env bash

##########################################################################################
#
# Target:
# For develop to be more easier to run testing via *pytest*.
#
# Description:
# It does 2 things: run script for getting testing items and run the testing via tool *pytest*.
# This bash file must to receive a argument *testing_type* which is the key condition to let
# script runs unit test or integration test.
#
# Allowable argument:
# * unit-test: Get and run unit test.
# * integration-test: Get and run integration test.
#
##########################################################################################

set -exm
testing_type=$1
echo "⚙️ It would run the '$testing_type' of the Python package PyMock-Server."

echo "🔍 Get the testing items ... ⏳"

# GitHub repro about the template of Python project CI/CD
# Refer: https://github.com/Chisanan232/GitHub-Action_Reusable_Workflows-Python
GitHub_Org=Chisanan232
GitHub_Repro=GitHub-Action_Reusable_Workflows-Python
GitHub_Repro_Branch=master

Scripts_Dir=./scripts/ci
Test_Running_Script=get-all-tests.sh

echo "🔍 Check whether it has necessary shell script '$Test_Running_Script' in '$Scripts_Dir/' directory or not."
# shellcheck disable=SC2010
test_running_script=$(ls "$Scripts_Dir" | grep -E "$Test_Running_Script" || true )
if [ "$test_running_script" == "" ]; then
    echo "⚠️ It should have shell script file '$Test_Running_Script' in '$Scripts_Dir/' directory of your project in HitHub."
    echo "Start to download the shell script file from repository 'GitHub-Action_Reusable_Workflows-Python' ..."
    curl https://raw.githubusercontent.com/$GitHub_Org/$GitHub_Repro/$GitHub_Repro_Branch/$Scripts_Dir/$Test_Running_Script --output $Scripts_Dir/$Test_Running_Script
    # wait for 3 second for downloading shell script
    sleep 3

    # check again
    # shellcheck disable=SC2010
    shell_script_file=$(ls "$Scripts_Dir" | grep -E "$Test_Running_Script" || true)
    if [ "$shell_script_file" == "" ]; then
        echo "❌️ It still cannot find the shell script file '$Test_Running_Script' in '$Scripts_Dir/' directory of your project in HitHub."
        exit 1
    else
        echo "✅ It already has shell script '$Test_Running_Script' in '$Scripts_Dir/' directory for running test."
    fi
else
    echo "✅ It already has shell script '$Test_Running_Script' in '$Scripts_Dir/' directory for running test."
fi

if echo "$testing_type" | grep -q "unit-test";
then
    test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/unit_test/ windows | sed "s/\"//g" | sed 's/^//')
elif echo "$testing_type" | grep -q "integration-test";
then
    test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/integration_test/ windows | sed "s/\"//g" | sed 's/^//')
elif echo "$testing_type" | grep -q "system-test";
then
    test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/system_test/ windows | sed "s/\"//g" | sed 's/^//')
elif echo "$testing_type" | grep -q "all-test";
then
    unit_test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/unit_test/ windows | sed "s/\"//g" | sed 's/^//')
    integration_test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/integration_test/ windows | sed "s/\"//g" | sed 's/^//')
    system_test_path=$(bash "$Scripts_Dir/$Test_Running_Script" ./test/system_test/ windows | sed "s/\"//g" | sed 's/^//')
    test_path="$unit_test_path $integration_test_path $system_test_path"
else
    test_path='error'
fi

if echo $test_path | grep -q "error";
then
  echo "❌ Got error when it tried to get testing items... 😱"
  exit 1
else
  echo "🎉🎊🍾 Get the testing items successfully!"
  echo "📄 The testing items are: "
  # shellcheck disable=SC2086
  echo $test_path

  echo "🤖⚒ It would start to run testing with Python testing framework *pytest*."
  # shellcheck disable=SC2086
  pytest $test_path
fi
