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
        'quick-start/cli-usage',
      ],
    },
    {
      type: 'category',
      label: '🧑‍💻 API References',
      items: [
        'api-references/api-references',
        {
          type: 'category',
          label: 'Web Server',
          items: [
            'api-references/web-server/web-apis',
            'api-references/web-server/webhooks-integration',
            {
              type: 'category',
              label: 'Endpoints',
              items: [
                'api-references/web-server/endpoints/web-api-health-check',
                'api-references/web-server/endpoints/clickup-webhooks',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'MCP Server',
          items: [
            'api-references/mcp-server/mcp-apis',
            'api-references/mcp-server/mcp-errors-and-retries',
            {
              type: 'category',
              label: 'Tools',
              items: [
                'api-references/mcp-server/tools/workspace-mcp-api',
                'api-references/mcp-server/tools/team-mcp-api',
                'api-references/mcp-server/tools/space-mcp-api',
                'api-references/mcp-server/tools/folder-mcp-api',
                'api-references/mcp-server/tools/list-mcp-api',
                'api-references/mcp-server/tools/task-mcp-api',
                'api-references/mcp-server/tools/analytics-mcp-api',
              ],
            },
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
