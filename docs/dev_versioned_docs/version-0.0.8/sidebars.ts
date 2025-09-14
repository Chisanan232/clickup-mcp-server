import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Dev section
 */
const sidebars: SidebarsConfig = {
  dev: [
    'development', // This matches the explicit ID in the frontmatter
    'requirements',
    'workflow',
    'coding-style',
    'architecture',
    {
      type: 'category',
      label: 'CI/CD Workflows',
      collapsed: false,
      items: [
        'ci-cd/index',
        'ci-cd/continuous-integration',
        'ci-cd/release-system',
        'ci-cd/documentation-deployment',
        'ci-cd/reusable-workflows',
        'ci-cd/additional-ci-workflows',
        'ci-cd/developer-guide',
      ],
    },
  ],
};

export default sidebars;
