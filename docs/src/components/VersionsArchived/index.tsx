import React from 'react';
import Link from '@docusaurus/Link';
import {useAllDocsData} from '@docusaurus/plugin-content-docs/client';
import {useActivePlugin} from '@docusaurus/plugin-content-docs/client';
import Translate from '@docusaurus/Translate';
import {ThemeClassNames} from '@docusaurus/theme-common';
import styles from './styles.module.css';

interface VersionInfo {
  name: string;
  label: string;
  banner?: string;
  badge?: string;
  docs: {path: string}[];
  isLast: boolean;
  isFirst: boolean;
}

interface PluginVersionInfo {
  pluginId: string;
  pluginTitle?: string;
  versions: VersionInfo[];
  latestVersion: VersionInfo;
}

export default function VersionsArchived(): JSX.Element {
  // Get all docs plugin data
  const allDocsData = useAllDocsData();
  
  // Configuration - you can customize these in docusaurus.config.ts
  const pluginTitles = {
    docs: 'User Guide',
    dev: 'Developer Guide',
    // Add other plugin titles here
  };

  // Base URL for GitHub releases - update this to the appropriate repository URL
  const releaseBaseUrl = 'https://github.com/Chisanan232/clickup-mcp-server/releases/tag/v';

  // Process version data for each plugin
  const pluginsVersionInfo = Object.keys(allDocsData).map((pluginId) => {
    const docsData = allDocsData[pluginId];
    const versions = docsData.versions;
    
    // Get the latest stable version (the first non-next version)
    const latestVersion = versions.find((version) => version.name !== 'current') || versions[0];
    
    return {
      pluginId,
      pluginTitle: pluginTitles[pluginId] || pluginId,
      versions,
      latestVersion,
    };
  });

  // Helper function to get release URL for a version
  const getReleaseUrl = (version: string): string => {
    // Skip "next" and "current" versions for release notes
    if (version === 'next' || version === 'current') {
      return `${releaseBaseUrl}latest`;
    }
    return `${releaseBaseUrl}${version}`;
  };

  return (
    <div className={styles.versionsContainer}>
      {pluginsVersionInfo.map((pluginInfo) => (
        <div key={pluginInfo.pluginId} className={styles.pluginSection}>
          <h2 className={styles.pluginTitle}>
            {pluginInfo.pluginTitle} Documentation
          </h2>

          {/* Current/Latest version section */}
          <div className={styles.versionSection}>
            <h3 className={styles.versionSectionTitle}>
              <Translate
                id="versions.current"
                description="The heading for the current version"
              >
                Current version (Stable)
              </Translate>
            </h3>
            <p className={styles.versionSectionDescription}>
              <Translate
                id="versions.currentVersionDescription"
                description="The description of the current stable version"
              >
                Here you can find the documentation for current released version.
              </Translate>
            </p>
            <div className={styles.versionRow}>
              <div className={styles.versionItem}>
                {pluginInfo.versions.find(v => v.name === 'current')?.label || 'Latest'}
              </div>
              <div className={styles.versionLinks}>
                <Link
                  className={styles.versionLink}
                  to={pluginInfo.versions.find(v => v.name === 'current')?.docs[0]?.path || `/${pluginInfo.pluginId}`}>
                  Documentation
                </Link>
                <Link
                  className={`${styles.versionLink} ${styles.releaseNotesLink}`}
                  to={getReleaseUrl('current')}
                  target="_blank"
                  rel="noopener noreferrer">
                  <Translate
                    id="versions.releaseNotes"
                    description="The label for release notes link"
                  >
                    Release Notes
                  </Translate>
                </Link>
              </div>
            </div>
          </div>

          {/* Next version section - only if it exists */}
          {pluginInfo.versions.some(version => version.name === 'next') && (
            <div className={styles.versionSection}>
              <h3 className={styles.versionSectionTitle}>
                <Translate
                  id="versions.next"
                  description="The heading for the next version"
                >
                  Next version (Unreleased)
                </Translate>
              </h3>
              <p className={styles.versionSectionDescription}>
                <Translate
                  id="versions.nextVersionDescription"
                  description="The description of the next version"
                >
                  Here you can find the documentation for work-in-process unreleased version.
                </Translate>
              </p>
              <div className={styles.versionRow}>
                <div className={styles.versionItem}>
                  <span>
                    {pluginInfo.versions.find(v => v.name === 'next')?.label || 'Next'}
                  </span>
                  <span className={styles.badge}>Next</span>
                </div>
                <div className={styles.versionLinks}>
                  <Link
                    className={styles.versionLink}
                    to={pluginInfo.versions.find(v => v.name === 'next')?.docs[0]?.path || `/${pluginInfo.pluginId}/next`}>
                    Documentation
                  </Link>
                  <Link
                    className={`${styles.versionLink} ${styles.releaseNotesLink}`}
                    to="https://github.com/Chisanan232/clickup-mcp-server/commits/master"
                    target="_blank"
                    rel="noopener noreferrer">
                    <Translate
                      id="versions.devChanges"
                      description="The label for development changes link"
                    >
                      Development Changes
                    </Translate>
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* Past versions section */}
          {pluginInfo.versions.some(version => version.name !== 'current' && version.name !== 'next') && (
            <div className={styles.versionSection}>
              <h3 className={styles.versionSectionTitle}>
                <Translate
                  id="versions.archived"
                  description="The heading for the archived versions"
                >
                  Past versions (Not maintained anymore)
                </Translate>
              </h3>
              <p className={styles.versionSectionDescription}>
                {/* Use regular text with no translation for dynamic content */}
                Here you can find documentation for previous versions of {pluginInfo.pluginTitle}.
              </p>
              
              {pluginInfo.versions
                .filter(version => version.name !== 'current' && version.name !== 'next')
                .map(version => (
                  <div key={version.name} className={styles.versionRow}>
                    <div className={styles.versionItem}>
                      {version.label}
                      {version.banner === 'unmaintained' && (
                        <span className={`${styles.badge} ${styles.unmaintained}`}>Unmaintained</span>
                      )}
                    </div>
                    <div className={styles.versionLinks}>
                      <Link
                        className={styles.versionLink}
                        to={version.docs[0]?.path || `/${pluginInfo.pluginId}/${version.name}`}>
                        Documentation
                      </Link>
                      <Link
                        className={`${styles.versionLink} ${styles.releaseNotesLink}`}
                        to={getReleaseUrl(version.name)}
                        target="_blank"
                        rel="noopener noreferrer">
                        <Translate
                          id="versions.releaseNotes"
                          description="The label for release notes link"
                        >
                          Release Notes
                        </Translate>
                      </Link>
                    </div>
                  </div>
                ))
              }
            </div>
          )}
        </div>
      ))}

      <div className={styles.allVersionsLink}>
        <Link to="/" className={styles.homeLink}>
          <Translate
            id="versions.goHome"
            description="The label for the link to go to home page"
          >
            Go to homepage
          </Translate>
        </Link>
      </div>
    </div>
  );
}
