### 🎉 New feature

1. Support complete golden user journeys for ClickUp MCP server.
   1. Implement the API clients with complete features for the MCP tools.
   2. Add the MCP tools.
      1. ClickUp team level features (get info only)
      2. ClickUp workspace level features (get info only)
      3. ClickUp space level features (get, create, update, delete)
      4. ClickUp folder level features (get, create, update, delete)
      5. ClickUp list level features (get, create, update, delete)
      6. ClickUp task level features (get, create, update, delete)
2. Support basic user journeys for ClickUp webhook features in the MCP server.
   1. Implement the webhook endpoint for ClickUp service.
   2. Provide the webhook event handlers.
      1. Provide the Pythonic style webhook event handlers.
      2. Provide the OOP style webhook event handlers.
   3. Implement the message queue components for the MCP server.


### 🪲 Bug Fix

#### 🙋‍♂️ For production

1. 💣 Critical bugs: (0)
   1. NaN
2. 🦠 Major bugs: (1)
   1. It only accepts to load the secret info from the command line option *--token*. ([PR#208])
3. 🐛 Mirror bugs: (0)
   1. NaN

[PR#208]: https://github.com/Chisanan232/clickup-mcp-server/pull/208

#### 👨‍💻 For development

1. Use the incorrect APIs to get the ClickUp API specification configuration. ([PR#187], [PR#192]).
2. CI workflow cannot upload README info to Docker Hub. ([PR#142])

[PR#187]: https://github.com/Chisanan232/clickup-mcp-server/pull/187
[PR#192]: https://github.com/Chisanan232/clickup-mcp-server/pull/192
[PR#142]: https://github.com/Chisanan232/clickup-mcp-server/pull/142


### 🍀 Improvement

1. Extract the long and big content about CI/CD workflows as a single section. ([PR#122])
2. Add a new CI workflow checks the documentation building process. ([PR#144])
3. Align all the workflows to reuse the GitHub Action reusable workflow repo. ([PR#157])
4. Fix all the warnings in the documentation building. ([PR#160])
5. Align the document content about the changes of aligning to reuse the GitHub Action reusable workflow repo. ([PR#161])

[PR#122]: https://github.com/Chisanan232/clickup-mcp-server/pull/122
[PR#144]: https://github.com/Chisanan232/clickup-mcp-server/pull/144
[PR#157]: https://github.com/Chisanan232/clickup-mcp-server/pull/157
[PR#160]: https://github.com/Chisanan232/clickup-mcp-server/pull/160
[PR#161]: https://github.com/Chisanan232/clickup-mcp-server/pull/161


### 🤖 Upgrade dependencies

1. Upgrade the Python dependencies.
2. Upgrade pre-commit dependencies.
3. Upgrade the CI reusable workflows.
