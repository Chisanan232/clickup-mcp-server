#!/usr/bin/env bash

#set -ex

# The file paths for auto-tag (git tag) and auto-release (GitHub release info)
Auto_Tag_And_Release_Dir=.github/tag_and_release
Auto_Tag_And_Release_Flag=release-auto-flag.txt
Auto_Release_Title=release-title.md
Auto_Release_Content=release-notes.md

# Check whether it has 'release-notes.md' or 'release-title.md' in the target directory '.github'.
has_auto_release_flag=$(ls "$Auto_Tag_And_Release_Dir" | grep -E "$Auto_Tag_And_Release_Flag")
if [ "$has_auto_release_flag" == "" ]; then
    echo "⚠️ It should have *$Auto_Tag_And_Release_Flag* in '$Auto_Tag_And_Release_Dir/' directory of your project in HitHub."
    exit 0
else
    auto_release_flag=$(cat "$Auto_Tag_And_Release_Dir/$Auto_Tag_And_Release_Flag")
    if [ "$auto_release_flag" == false ]; then
        echo "💤 Auto-release flag is 'false' so it won't build git tag or create GitHub release."
        exit 0
    fi
fi

has_release_notes=$(ls "$Auto_Tag_And_Release_Dir" | grep -E "$Auto_Release_Content")
has_release_title=$(ls "$Auto_Tag_And_Release_Dir" | grep -E "$Auto_Release_Title")
if [ "$has_release_notes" == "" ]; then
    echo "❌ It should have *$Auto_Release_Content* in '$Auto_Tag_And_Release_Dir/' directory of your project in HitHub."
    exit 1
fi
if [ "$has_release_title" == "" ]; then
    echo "❌ It should have *$Auto_Release_Title* in '$Auto_Tag_And_Release_Dir/' directory of your project in HitHub."
    exit 1
fi


Input_Arg_Debug_Mode=$1

keep_release="$KEEP_RELEASE_IF_PRE_VERSION"

if [ "$Input_Arg_Debug_Mode" == "" ]; then
    Input_Arg_Debug_Mode=true
fi

#Current_Branch=$(git branch --show-current)
 # # # For debug
#echo "Verify the git branch info"
#git branch --list | cat
#echo "Verify all the git branch info"
#git branch -a | cat
#echo "Verify the git remote info"
#git remote -v
#echo "Get the current git branch info"

# This is the global value to provide after-handle to use
Current_Branch=$(git branch --list | cat | grep -E '\* ([a-zA-Z0-9]{1,16})' | grep -E -o '([a-zA-Z0-9]{1,16})')
echo "🔎 🌳  Current git branch: $Current_Branch"

git config --global user.name "Chisanan232"
git config --global user.email "chi10211201@cycu.org.tw"
git_global_username=$(git config --global user.name)
git_global_user_email=$(git config --global user.email)
echo "🔎 🌳  Current git name: $git_global_username"
echo "🔎 🌳  Current git email: $git_global_user_email"

git pull
echo "📩 🌳  git pull done"

declare Tag_Version    # This is the return value of function 'get_latest_version_by_git_tag'
get_latest_version_by_git_tag() {
    # # # # The types to get version by tag: 'git' or 'github'
    get_version_type=$1

    if [ "$get_version_type" == "git" ]; then
        echo "🔎 🌳 🏷 Get the version info from git tag."
        Tag_Version=$(git describe --tag --abbrev=0 --match "v[0-9]\.[0-9]\.[0-9]*" | grep -E -o '[0-9]\.[0-9]\.[0-9]*')
    elif [ "$get_version_type" == "github" ]; then
        echo "🔎 🐙 🐈 🏷  Get the version info from GitHub release."
        github_release=$(curl -s https://api.github.com/repos/Chisanan232/GitHub-Action_Reusable_Workflows-Python/releases/latest | jq -r '.tag_name')
        Tag_Version=$(echo "$github_release" | grep -E -o '[0-9]\.[0-9]\.[0-9]*')
    else
        echo "❌ Currently, it only has 2 valid options could use: 'git' or 'github'."
        exit 1
    fi
}


declare New_Release_Version    # This is the return value of function 'generate_new_version_as_tag'
declare New_Release_Tag    # This is the return value of function 'generate_new_version_as_tag'
generate_new_version_as_tag() {
    project_type=$1
    echo "🔎 🐍 📦  Get the new version info from UV version command."
    # Use uv version --short to get just the version number directly
    New_Release_Version=$(uv version --short 2>/dev/null || echo "")
    if [ "$New_Release_Version" == "" ]; then
        echo "❌ Failed to get version from 'uv version --short' command. Please ensure uv is installed and project has valid pyproject.toml"
        exit 1
    fi
    New_Release_Tag="v$New_Release_Version"
    echo "🔎 📃  Current Version from UV: $New_Release_Version"
}


build_git_tag_or_github_release() {
    # git event: push
    # all branch -> Build tag
    # master branch -> Build tag and create release
    project_type=$1
    generate_new_version_as_tag "$project_type"
    build_git_tag
    build_github_release
}


build_git_tag() {
    # git event: push
    # all branch -> Build tag
    # master branch -> Build tag and create release
    ensure_release_tag_is_not_empty

    if [ "$Input_Arg_Debug_Mode" == true ]; then
        echo " 🔍👀 [DEBUG MODE] Build git tag $New_Release_Tag in git branch '$Current_Branch'."
    else
        git tag -a "$New_Release_Tag" -m "$New_Release_Tag"
        git push -u origin --tags
    fi
    echo "🎉 🍻 🌳 🏷  Build git tag which named '$New_Release_Tag' with current branch '$Current_Branch' successfully!"
}


build_github_release() {
    # git event: push
    # all branch -> Build tag
    # master branch -> Build tag and create release
    ensure_release_tag_is_not_empty

    if [ "$Current_Branch" == "master" ]; then
        release_title=$(cat "$Auto_Tag_And_Release_Dir/$Auto_Release_Title")

        if [ "$Input_Arg_Debug_Mode" == true ]; then
            echo " 🔍👀 [DEBUG MODE] Create GitHub release with tag '$New_Release_Tag' and title '$release_title' in git branch '$Current_Branch'."
        else
            gh release create "$New_Release_Tag" --title "$release_title" --notes-file "$Auto_Tag_And_Release_Dir/$Auto_Release_Content"
        fi
    fi
        echo "🎉 🍻 🐙 🐈 🏷  Create GitHub release with title '$release_title' successfully!"
}


ensure_release_tag_is_not_empty() {
    if [ "$New_Release_Tag" == "" ]; then
        echo "❌ The new release tag it got is empty. Please check version info in your repository."
        exit 1
    else
        echo "✅  It gets new version info and it's *$New_Release_Tag*. It would keep running to set it."
    fi
}


tag_and_release_python_project() {
    git_tag=$(git describe --tag --abbrev=0 --match "v[0-9]\.[0-9]\.[0-9]*" | grep -o '[0-9]\.[0-9]\.[0-9]*')
    github_release=$(curl -s https://api.github.com/repos/Chisanan232/GitHub-Action_Reusable_Workflows-Python/releases/latest | jq -r '.tag_name')
    # shellcheck disable=SC2002
    generate_new_version_as_tag "python"

    build_git_tag=false
    create_github_release=false

    # 1. Compare the Python source code version and git tag, GitHub release version.
    if [ "$New_Release_Version" == "$git_tag" ]; then
        echo "✅  Version of git tag info are the same. So it verifies it has built and pushed before."
    else
        echo "⚠️  Version of git tag info are different. So it verifies it doesn't build and push before."
        build_git_tag=true
    fi

    if [ "$Current_Branch" == "master" ] && [ "$New_Release_Version" == "$github_release" ]; then
        echo "✅  Version of GitHub release info are the same. So it verifies it has built and pushed before."
    else
        echo "⚠️  Version of GitHub release info are different. So it verifies it doesn't build and push before."
        create_github_release=true
    fi

    # 1. -> Same -> 1-1. Does it have built and pushed before?.
    # 1. -> No (In generally, it should no) -> 1-2. Is it a pre-release version in source code?

    # 1-1. Yes, it has built and pushed. -> Doesn't do anything.
    # 1-1. No, it doesn't build and push before. -> Build and push directly.

    # 1-2. Yes, it's pre-release. -> Doesn't build and push. Just build git tag and GitHub release.
    # 1-2. No, it's not pre-release. -> It means that it's official version, e.g., 1.3.2 version. So it should build git tag and GitHub release first, and build and push.

    if [ "$build_git_tag" == true ] || [ "$create_github_release" == true ]; then

        echo "🔎 🐍 📦 Python package new release version: $New_Release_Version"
        is_pre_release_version=$(echo $New_Release_Version | grep -E -o '([\.-]*([a-zA-Z]{1,})+([0-9]{0,})*){1,}')
        echo "🔎 🤰 📦 is pre-release version: $is_pre_release_version"
        if [ "$is_pre_release_version" == "" ] || [ "$keep_release" == "TRUE" ]; then
            echo "🎓 🐍 📦 The version is a official-release."
            # do different things with different ranches
            # git event: push
            # all branch -> Build tag
            # master branch -> Build tag and create release
            echo "👷🏽‍♂️ 📌 Build tag and create GitHub release, also push code to PyPi"
            build_git_tag_or_github_release "python"
            echo "✅ 🎊 🥂 Done! This is Official-Release so please push source code to PyPi."
            echo "[Python] [Final Running Result] Official-Release"
        else
            echo "The version is a pre-release."
            # do different things with different ranches
            # git event: push
            # all branch -> Build tag
            # master branch -> Build tag and create release
            echo "👷🏽‍♂ ️📌 Build tag and create GitHub release only"
            build_git_tag_or_github_release "python"
            echo "✅ 🎊 🥂 Done! This is Pre-Release so please don't push this to PyPi."
            echo "[Python] [Final Running Result] Pre-Release"
        fi

    fi
}


# The truly running implementation of shell script
# # # # For Python package release
echo "🏃‍♂ ️🐍 𝌚 Run python package releasing process"
tag_and_release_python_project
