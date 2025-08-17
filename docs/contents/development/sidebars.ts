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
    'ci-cd',
  ],
};

export default sidebars;
