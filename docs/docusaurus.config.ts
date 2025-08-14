import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkGfm from 'remark-gfm';
import remarkMdxCodeMeta from 'remark-mdx-code-meta';

const config: Config = {
  title: 'ClickUp-MCP-Server',
  tagline: '🦾 A strong MCP server for ClickUp.',
  favicon: 'img/clickup-logo.png',

  // Set the production url of your site here
  url: 'https://chisanan232.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/clickup-mcp-server/',
  projectName: 'chisanan232.github.io',
  organizationName: 'chisanan232',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  onDuplicateRoutes: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
    format: 'detect',
    mdx1Compat: {
      comments: true,
      admonitions: true,
      headingIds: true,
    },
  },

  presets: [
    [
      'classic',
      {
        docs: false,
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'documentation',
        path: 'contents/document',
        routeBasePath: 'document',
        sidebarPath: './contents/document/sidebars.ts',
        sidebarCollapsible: true,
        editUrl:
          'https://github.com/Chisanan232/clickup-mcp-server/tree/master/docs/',
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'development',
        path: 'contents/development',
        routeBasePath: 'development',
        sidebarPath: './contents/development/sidebars.ts',
        sidebarCollapsible: true,
        editUrl:
          'https://github.com/Chisanan232/clickup-mcp-server/tree/master/docs/',
      },
    ],
  ],

  themes: [
    '@docusaurus/theme-mermaid',
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/clickup_mcp_server_logo.png',
    navbar: {
      title: 'ClickUp-MCP-Server',
      logo: {
        alt: 'My Site Logo',
        src: 'img/clickup_mcp_server_logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'documentation',
          position: 'left',
          label: 'Documentation',
          docsPluginId: 'documentation',
        },
        {
          type: 'docSidebar',
          sidebarId: 'development',
          position: 'left',
          label: 'Development',
          docsPluginId: 'development',
        },
        {
          href: 'https://github.com/Chisanan232/clickup-mcp-server',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: '/document/introduction',
            },
            {
              label: 'Development',
              to: '/development',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/Chisanan232/clickup-mcp-server/issues',
            },
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/Chisanan232/clickup-mcp-server/discussions',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub Repository',
              href: 'https://github.com/Chisanan232/clickup-mcp-server',
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} - PRESENT, ClickUp MCP Server is owned by <a href="https://github.com/Chisanan232">@Chisanan232</a>.<br />Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },

  // Add redirect for homepage
  staticDirectories: ['static'],
  // Homepage redirects to documentation
  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'canonical',
        href: 'https://chisanan232.github.io/clickup-mcp-server/document/introduction',
      },
    },
  ],
};

// Set homepage to redirect to documentation
config.scripts = [
  {
    src: '/clickup-mcp-server/js/dist/redirect-to-docs.js',
    async: false,
    defer: false,
  },
];

export default config;
