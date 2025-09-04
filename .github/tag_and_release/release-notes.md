### 🎉 New feature

1. Newborn of ClickUp MCP server project.
    ```shell
    >>> clickup-mcp-server --help
    usage: clickup-mcp-server [-h] [--host HOST] [--port PORT] [--log-level {debug,info,warning,error,critical}] [--reload] [--env ENV_FILE] [--token TOKEN]
                              [--transport {sse,http-streaming}]
    
    Run the ClickUp MCP FastAPI server
    
    options:
      -h, --help            show this help message and exit
      --host HOST           Host to bind the server to
      --port PORT           Port to bind the server to
      --log-level {debug,info,warning,error,critical}
                            Logging level
      --reload              Enable auto-reload for development
      --env ENV_FILE        Path to the .env file for environment variables
      --token TOKEN         ClickUp API token (overrides token from .env file if provided)
      --transport {sse,http-streaming}
                            Transport protocol to use for MCP (sse or http-streaming)
    ```


[//]: # (### 🔨 Breaking changes)

[//]: # ()
[//]: # (1. Deprecate Python 3.8 version support, will remove all code in next version. &#40;[PR#498]&#41;)


[//]: # (### 🪲 Bug Fix)

[//]: # ()
[//]: # (#### 🙋‍♂️ For production)

[//]: # ()
[//]: # (1. 💣 Critical bugs:)

[//]: # (   1. Command line tool cannot work finely because filtering logic cannot cover all scenarios. &#40;[PR#496]&#41;)

[//]: # (   2. Command line tool cannot work finely because missing Python dependency. &#40;[PR#498]&#41;)

[//]: # (2. 🦠 Major bugs:)

[//]: # (   1. The request checking process: &#40;[PR#493]&#41;)

[//]: # (      1. Error messages are incorrect which would deeply mislead developers.)

[//]: # (      2. The parameters data checking cannot work finely with array type parameters.)

[//]: # (   2. It set incorrect customized value at format property with subcommand line `pull`. &#40;[PR#487]&#41;)

[//]: # (   3. Generate incorrect data structure in API response. &#40;[PR#492]&#41;)

[//]: # (3. 🐛 Mirror bugs:)

[//]: # (   1. Command line option `--include-template-config` cannot work under subcommand line `pull`. &#40;[PR#485]&#41;)

[//]: # (   2. Default value cannot be set correctly if it's empty string value. &#40;[PR#484]&#41;)

[//]: # ()
[//]: # ([PR#484]: https://github.com/Chisanan232/PyFake-API-Server/pull/484)

[//]: # ([PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485)

[//]: # ([PR#487]: https://github.com/Chisanan232/PyFake-API-Server/pull/487)

[//]: # ([PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485)

[//]: # ([PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485)

[//]: # ([PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485)

[//]: # ([PR#492]: https://github.com/Chisanan232/PyFake-API-Server/pull/492)

[//]: # ([PR#493]: https://github.com/Chisanan232/PyFake-API-Server/pull/493)

[//]: # ([PR#496]: https://github.com/Chisanan232/PyFake-API-Server/pull/496)

[//]: # ([PR#498]: https://github.com/Chisanan232/PyFake-API-Server/pull/498)

#### 👨‍💻 For development

1. Provide the [development details] in [documentation].

[development details]: https://chisanan232.github.io/clickup-mcp-server/dev/next


[//]: # (### ♻️ Refactor)

[//]: # ()
[//]: # (1. content ...)


[//]: # (### 🍀 Improvement)

[//]: # ()
[//]: # (1. Clear the Pre-Commit configuration. &#40;[PR#481]&#41;)

[//]: # (2. Clear the CI workflow configurations. &#40;[PR#482]&#41;)

[//]: # (3. Let program could raise obvious error message if it misses some necessary values at initial process. &#40;[PR#486]&#41;)

[//]: # ()
[//]: # ([PR#481]: https://github.com/Chisanan232/PyFake-API-Server/pull/481)

[//]: # ([PR#482]: https://github.com/Chisanan232/PyFake-API-Server/pull/482)

[//]: # ([PR#486]: https://github.com/Chisanan232/PyFake-API-Server/pull/486)


### 📑 Docs

1. Provide the [details] in [documentation].

[details]: https://chisanan232.github.io/clickup-mcp-server/docs/next/introduction
[documentation]: https://chisanan232.github.io/clickup-mcp-server/


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

