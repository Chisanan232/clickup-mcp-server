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
            'api-references/web-apis/web-apis',
            'api-references/web-apis/web-api-health-check',
          ],
        },
        {
          type: 'category',
          label: 'MCP Server APIs',
          items: [
            'api-references/mcp-apis/mcp-apis',
            'api-references/mcp-apis/team-mcp-api',
            'api-references/mcp-apis/space-mcp-api',
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
