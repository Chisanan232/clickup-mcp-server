import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useLatestVersion, useDocById } from '@docusaurus/plugin-content-docs/client';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  
  // Get all versions from the docs plugin
  const allDocs = useLatestVersion('docs');
  const docsBasePath = '/docs';
  
  // Find the latest stable version (not "next")
  const stableVersion = allDocs?.versions?.find(version => version.name !== 'current' && version.name !== 'next');
  
  // Calculate the path to the stable documentation with fallbacks
  const stableDocsPath = stableVersion?.path || 
    (stableVersion?.name ? `${docsBasePath}/${stableVersion.name}/introduction` : `${docsBasePath}/next/introduction`);
  
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to={stableDocsPath}>
            ClickUp-MCP-Server Documentation
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
