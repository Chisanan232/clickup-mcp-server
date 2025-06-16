### 🎉 New feature

1. Support Python **3.13** version. ([PR#483])
2. Add new value format properties:
   1. ``static_value``: New strategy for setting fixed value. ([PR#489])
   2. ``format.static_value``: The specific fixed value for the strategy ``static_value``, includes this property in `format.variable`. ([PR#489], [PR#490], [PR#491])
   3. ``format.unique_element``: Only for array type value which could generate unique elements in array type property, includes this property in `format.variable`. ([PR#494])
3. Support API request could accept multiple different value formats, i.e., ISO format or Unix timestamp of datetime value. ([PR#488])

[PR#483]: https://github.com/Chisanan232/PyFake-API-Server/pull/483
[PR#488]: https://github.com/Chisanan232/PyFake-API-Server/pull/488
[PR#489]: https://github.com/Chisanan232/PyFake-API-Server/pull/489
[PR#490]: https://github.com/Chisanan232/PyFake-API-Server/pull/490
[PR#491]: https://github.com/Chisanan232/PyFake-API-Server/pull/491
[PR#494]: https://github.com/Chisanan232/PyFake-API-Server/pull/494


### 🔨 Breaking changes

1. Deprecate Python 3.8 version support, will remove all code in next version. ([PR#498])


### 🪲 Bug Fix

#### 🙋‍♂️ For production

1. 💣 Critical bugs:
   1. Command line tool cannot work finely because filtering logic cannot cover all scenarios. ([PR#496])
   2. Command line tool cannot work finely because missing Python dependency. ([PR#498])
2. 🦠 Major bugs:
   1. The request checking process: ([PR#493])
      1. Error messages are incorrect which would deeply mislead developers.
      2. The parameters data checking cannot work finely with array type parameters.
   2. It set incorrect customized value at format property with subcommand line `pull`. ([PR#487])
   3. Generate incorrect data structure in API response. ([PR#492])
3. 🐛 Mirror bugs:
   1. Command line option `--include-template-config` cannot work under subcommand line `pull`. ([PR#485])
   2. Default value cannot be set correctly if it's empty string value. ([PR#484])

[PR#484]: https://github.com/Chisanan232/PyFake-API-Server/pull/484
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#487]: https://github.com/Chisanan232/PyFake-API-Server/pull/487
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#492]: https://github.com/Chisanan232/PyFake-API-Server/pull/492
[PR#493]: https://github.com/Chisanan232/PyFake-API-Server/pull/493
[PR#496]: https://github.com/Chisanan232/PyFake-API-Server/pull/496
[PR#498]: https://github.com/Chisanan232/PyFake-API-Server/pull/498

#### 👨‍💻 For development

1. The file path regular expression is incorrect at documentation CI workflow. ([PR#499])

[PR#499]: https://github.com/Chisanan232/PyFake-API-Server/pull/499


[//]: # (### ♻️ Refactor)

[//]: # ()
[//]: # (1. content ...)


### 🍀 Improvement

1. Clear the Pre-Commit configuration. ([PR#481])
2. Clear the CI workflow configurations. ([PR#482])
3. Let program could raise obvious error message if it misses some necessary values at initial process. ([PR#486])

[PR#481]: https://github.com/Chisanan232/PyFake-API-Server/pull/481
[PR#482]: https://github.com/Chisanan232/PyFake-API-Server/pull/482
[PR#486]: https://github.com/Chisanan232/PyFake-API-Server/pull/486


### 📑 Docs

1. Update the content for new command line options. ([PR#487])

[PR#487]: https://github.com/Chisanan232/PyFake-API-Server/pull/497


[//]: # (### 🤖 Upgrade dependencies)

[//]: # ()
[//]: # ([//]: # &#40;1. Upgrade the Python dependencies.&#41;)
[//]: # ()
[//]: # (1. Upgrade pre-commit dependencies.)

[//]: # (3. Upgrade the CI reusable workflows.)

[//]: # ()
[//]: # (   1. Upgrade SonarQube and update its configuration)

[//]: # ()
[//]: # (   2. Update the usage because upgrading the artifact actions)

[//]: # (### 🚮Deprecate)

[//]: # ()
[//]: # (1. Deprecate and remove version 0.3.0 because it has multiple issue, and it cannot upload same version file to PyPI.)
