import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Docs section
 */
const sidebars: SidebarsConfig = {
  docs: [
    'introduction',
    {
      type: 'category',
      label: '🤟 Quickly Start',
      collapsed: false,
      items: [
        'quick-start/quick-start',
        'quick-start/requirements',
        'quick-start/installation',
        'quick-start/how-to-run',
      ],
    },
    {
      type: 'category',
      label: '🧑‍💻 API References',
      items: [
        'api-references/api-references',
        {
          type: 'category',
          label: 'Web APIs',
          items: [
            'api-references/web-server/web-apis',
            {
              type: 'category',
              label: 'Endpoints',
              items: [
                'api-references/web-server/endpoints/web-api-health-check',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'MCP Server APIs',
          items: [
            'api-references/mcp-server/mcp-apis',
            'api-references/mcp-server/mcp-errors-and-retries',
            'api-references/mcp-server/workspace-mcp-api',
            'api-references/mcp-server/team-mcp-api',
            'api-references/mcp-server/space-mcp-api',
            'api-references/mcp-server/folder-mcp-api',
            'api-references/mcp-server/list-mcp-api',
            'api-references/mcp-server/task-mcp-api',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: '👋 Welcome to contribute',
      items: [
        'contribute/contribute',
        'contribute/report-bug',
        'contribute/request-changes',
        'contribute/discuss',
      ],
    },
    'changelog',
  ],
};

export default sidebars;
