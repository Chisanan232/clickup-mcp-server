---
title: ClickUp API Specification Has Changed
labels: api, breaking-change, needs-attention
assignees: ''
---

⚠️ **ClickUp API Specification Has Changed** ⚠️

The automated check has detected changes in the ClickUp API specification. The client and local API specification need to be updated.

## Action Required

1. Run the API specification checker locally to see the changes:
   ```bash
   python scripts/ci/api_spec_checker.py --verbose
   ```

2. Update the local API specification:
   ```bash
   python scripts/ci/api_spec_checker.py --update
   ```

3. Review the changes and update the API client accordingly

4. Create a pull request with these changes

## Why This Is Important

Keeping our API client in sync with the official ClickUp API specification ensures that:
- We're aware of new features we could leverage
- We catch breaking changes before they affect our production systems
- Our client implementation remains compatible with the API

Please prioritize this update to avoid potential issues with API integration.
