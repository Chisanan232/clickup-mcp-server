/**
 * UnifiedVersionsDropdownNavbarItem - Custom Docusaurus component
 * 
 * Combines version dropdowns from multiple docs plugins into a single dropdown
 * with grouped version options by plugin.
 */
import React from 'react';
import clsx from 'clsx';
import { useAllDocsData, useDocsPreferredVersion } from '@docusaurus/plugin-content-docs/client';
import { useActiveDocContext } from '@docusaurus/plugin-content-docs/client';
import { translate } from '@docusaurus/Translate';
import { useLocation } from '@docusaurus/router';
import DropdownNavbarItem from '@theme/NavbarItem/DropdownNavbarItem';
import DefaultNavbarItem from '@theme/NavbarItem/DefaultNavbarItem';
import { useThemeConfig } from '@docusaurus/theme-common';
import type { Props } from '@theme/NavbarItem/DropdownNavbarItem';
import styles from './styles.module.css';

// Interface for custom props used by the unified versions dropdown
interface UnifiedVersionsDropdownNavbarItemProps extends Props {
  pluginIds: string[];
  dropdownItemsBefore?: JSX.Element[];
  dropdownItemsAfter?: JSX.Element[];
  pluginTitles?: Record<string, string>;
  showBadges?: boolean;
  showNextLabel?: boolean;
  showUnmaintainedLabel?: boolean;
  showLatestVersion?: boolean;
  showDividers?: boolean;
}

// Type for version information collected from each docs plugin
interface PluginVersionInfo {
  pluginId: string;
  pluginTitle: string;
  versions: {
    name: string;
    label: string;
    banner: string | null;
    badge: boolean | undefined;
    className: string | undefined;
    path: string;
    docs: { id: string; path: string }[];
  }[];
  activeVersion: {
    name: string;
    label: string;
    banner: string | null;
    badge: boolean | undefined;
    className: string | undefined;
    path: string;
    docs: { id: string; path: string }[];
  } | null;
  latestDocVersion: {
    name: string;
    label: string;
    banner: string | null;
    badge: boolean | undefined;
    className: string | undefined;
    path: string;
    docs: { id: string; path: string }[];
  } | null;
  hasActiveVersion: boolean;
}

// Main component
export default function UnifiedVersionsDropdownNavbarItem({
  pluginIds,
  pluginTitles = {},
  mobile = false,
  dropdownItemsBefore = [],
  dropdownItemsAfter = [],
  showBadges = true,
  showNextLabel = true,
  showUnmaintainedLabel = true,
  showLatestVersion = true,
  showDividers = true,
  ...props
}: UnifiedVersionsDropdownNavbarItemProps): JSX.Element {
  const allDocsData = useAllDocsData();
  const location = useLocation();

  // Gather version information from all specified plugins
  const pluginsVersionInfo: PluginVersionInfo[] = pluginIds
    .filter(pluginId => {
      // Filter out plugins that don't exist or have no versions
      const docsData = allDocsData[pluginId];
      return docsData && docsData.versions.length > 0;
    })
    .map(pluginId => {
      // Get docs data for this plugin
      const docsData = allDocsData[pluginId];
      const versions = docsData?.versions || [];

      // Try to determine active version
      let activeVersion = null;
      let activeDoc = null;
      try {
        const activeDocContext = useActiveDocContext(pluginId);
        activeVersion = activeDocContext?.activeVersion || null;
        activeDoc = activeDocContext?.activeDoc || null;
      } catch (e) {
        // Ignore errors if hooks fail
        console.error(`Error getting active doc context for ${pluginId}:`, e);
      }

      // Try to get preferred version
      let preferredVersion = null;
      try {
        const preferredVersionData = useDocsPreferredVersion(pluginId);
        preferredVersion = preferredVersionData?.preferredVersion || null;
      } catch (e) {
        // Ignore errors if hooks fail
        console.error(`Error getting preferred version for ${pluginId}:`, e);
      }
      
      // Get latest version safely (usually the one with name='current' or the first one)
      let latestDocVersion = null;
      if (versions && versions.length > 0) {
        latestDocVersion = versions.find(version => version?.name === 'current') || versions[0] || null;
      }

      // Default title for the plugin if not specified
      const defaultTitle = docsData?.pluginData?.name || pluginId;
      const pluginTitle = pluginTitles[pluginId] || defaultTitle;

      // Determine if there's an active version for this plugin
      let hasActiveVersion = false;
      const currentPath = location.pathname;

      if (activeVersion) {
        // If activeVersion is directly set, trust it
        hasActiveVersion = true;
      } else if (versions && versions.length > 0) {
        // Otherwise check if current path includes this plugin's path
        hasActiveVersion = versions.some(version => {
          return version?.docs?.some(doc => doc?.path && currentPath.includes(doc.path));
        });
      }

      return {
        pluginId,
        pluginTitle,
        versions,
        activeVersion,
        latestDocVersion,
        hasActiveVersion,
      };
    });
  
  // Create dropdown items
  const dropdownItems: JSX.Element[] = [];
  
  // Add items specified to come before
  if (dropdownItemsBefore.length > 0) {
    dropdownItems.push(...dropdownItemsBefore);
  }
  
  // For each plugin, add its versions
  pluginsVersionInfo.forEach((pluginInfo, pluginIndex) => {
    const {
      pluginId,
      pluginTitle,
      versions,
      activeVersion,
      latestDocVersion,
      hasActiveVersion,
    } = pluginInfo;

    // Only add plugin versions if there are any
    if (versions && versions.length > 0) {
      // Add divider before each plugin section except the first
      if (showDividers && pluginIndex > 0) {
        dropdownItems.push({
          type: 'html',
          key: `divider-${pluginId}`,
          value: `<div class="${styles.divider}"></div>`,
        });
      }
      
      // Add plugin title as a header
      dropdownItems.push({
        type: 'html',
        key: `header-${pluginId}`,
        value: `<div class="${styles.groupHeader}">${pluginTitle || pluginId}</div>`,
      });

      // Add all versions for this plugin
      versions.forEach((version) => {
        // Skip if version is invalid
        if (!version) return;
        
        // Is this the active version for the current plugin?
        const isActivePluginVersion = hasActiveVersion && 
          activeVersion?.name === version.name;
          
        // Is this the latest version?
        const isLatest = latestDocVersion && version.name === latestDocVersion.name;
          
        // Create version label with badges if needed
        let versionLabel = version.label || version.name;
        
        // URL for this version - ensure we have a valid path
        const firstDocPath = version.docs?.[0]?.path;
        const fallbackPath = `/docs/${version.path || ''}`;
        const versionUrl = firstDocPath || fallbackPath;
        
        // For badge rendering, we need to handle it differently
        if (showBadges && isLatest && showNextLabel && version.name === 'current') {
          // Use HTML for badge (with proper classes for styling)
          dropdownItems.push({
            type: 'html',
            key: `${pluginId}-${version.name}`,
            className: clsx(
              {
                'dropdown__link--active': isActivePluginVersion,
                [styles.dropdownItemActive]: isActivePluginVersion,
                [styles.latestVersion]: isLatest && !isActivePluginVersion,
              },
            ),
            value: `<a href="${versionUrl}" class="dropdown__link">${versionLabel} <span class="${styles.badge}">Next</span></a>`,
          });
        } else if (showBadges && showUnmaintainedLabel && version.banner === 'unmaintained') {
          // Use HTML for unmaintained badge
          dropdownItems.push({
            type: 'html',
            key: `${pluginId}-${version.name}`,
            className: clsx(
              {
                'dropdown__link--active': isActivePluginVersion,
                [styles.dropdownItemActive]: isActivePluginVersion,
                [styles.latestVersion]: isLatest && !isActivePluginVersion,
              },
            ),
            value: `<a href="${versionUrl}" class="dropdown__link">${versionLabel} <span class="${clsx(styles.badge, styles.unmaintained)}">Unmaintained</span></a>`,
          });
        } else {
          // Regular version without badge - use standard item type
          dropdownItems.push({
            type: 'default',
            key: `${pluginId}-${version.name}`,
            className: clsx(
              {
                'dropdown__link--active': isActivePluginVersion,
                [styles.dropdownItemActive]: isActivePluginVersion,
                [styles.latestVersion]: isLatest && !isActivePluginVersion,
              },
            ),
            label: versionLabel,
            to: versionUrl,
            isDropdownItem: true,
          });
        }
      });
    }
  });
  
  // Add divider before "All versions" link
  if (dropdownItems.length > 0) {
    dropdownItems.push({
      type: 'html',
      key: 'divider-all-versions',
      value: `<div class="${styles.allVersionsSeparator}"></div>`,
    });
    
    // Add "All versions" link at the bottom
    dropdownItems.push({
      type: 'default',
      key: 'all-versions',
      label: translate({
        id: 'theme.navbar.allVersions',
        message: 'All versions',
        description: 'The label for the link to all versions in dropdown',
      }),
      to: '/versions',
      isDropdownItem: true,
    });
  }
  
  // Add items specified to come after
  if (dropdownItemsAfter.length > 0) {
    if (showDividers && pluginsVersionInfo.some(info => info.versions.length > 0)) {
      dropdownItems.push({
        type: 'html',
        key: 'divider-after',
        value: `<div class="${styles.divider}"></div>`,
      });
    }
    dropdownItems.push(...dropdownItemsAfter);
  }

  // Create label for the dropdown button
  const dropdownLabel = translate({
    id: 'theme.navbar.unifiedVersionsDropdown.label',
    message: 'Versions',
    description: 'The label for the navbar unified versions dropdown',
  });

  // Return the dropdown component
  return (
    <DropdownNavbarItem
      {...props}
      mobile={mobile}
      label={dropdownLabel}
      items={dropdownItems}
    />
  );
}
