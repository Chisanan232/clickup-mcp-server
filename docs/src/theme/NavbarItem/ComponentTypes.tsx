/**
 * Custom navbar item type registration for Docusaurus
 * Extends the default components instead of replacing them
 */
import React from 'react';
import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import UnifiedVersionsDropdownNavbarItem from '@theme/NavbarItem/UnifiedVersionsDropdownNavbarItem';

export default {
  ...ComponentTypes,
  'custom-unifiedVersions': UnifiedVersionsDropdownNavbarItem,
};
