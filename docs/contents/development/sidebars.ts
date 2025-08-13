import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Development section
 */
const sidebars: SidebarsConfig = {
  development: [
    'development', // This matches the explicit ID in the frontmatter
    'requirements',
    'workflow',
    'coding-style',
    'architecture',
    'ci-cd',
  ],
};

export default sidebars;
