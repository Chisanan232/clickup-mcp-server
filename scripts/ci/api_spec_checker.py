#!/usr/bin/env python3
"""
ClickUp API Specification Change Detector

This script checks the ClickUp OpenAPI specification for changes by comparing
the remote specification with a locally stored copy.

If changes are detected, it will exit with a non-zero status code and print the differences.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, ConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api_spec_checker")


# DTO Models
class InfoDTO(BaseModel):
    """DTO model for OpenAPI info section."""

    title: str
    description: Optional[str] = None
    version: str


class PathItemDTO(BaseModel):
    """DTO model for OpenAPI path item."""

    model_config = ConfigDict(extra="allow")

    # Methods
    get: Optional[Dict[str, Any]] = None
    post: Optional[Dict[str, Any]] = None
    put: Optional[Dict[str, Any]] = None
    delete: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    head: Optional[Dict[str, Any]] = None
    patch: Optional[Dict[str, Any]] = None
    trace: Optional[Dict[str, Any]] = None


class ApiSpecificationDTO(BaseModel):
    """DTO model for OpenAPI specification."""

    model_config = ConfigDict(extra="allow")

    openapi: str
    info: InfoDTO
    paths: Dict[str, PathItemDTO] = {}

    def __eq__(self, other: Any) -> bool:
        """Compare two API specifications for equality."""
        if not isinstance(other, ApiSpecificationDTO):
            return False

        # Convert both to dict for deep comparison
        return self.model_dump() == other.model_dump()


# Domain Models
class ChangeType(str, Enum):
    """Type of change detected in API specification."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass
class SpecificationDifference:
    """Represents a difference between two API specifications."""

    path: str
    change_type: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


@dataclass
class SpecificationComparisonResult:
    """Result of comparing two API specifications."""

    has_changes: bool
    differences: List[SpecificationDifference]


class ApiSpecChecker:
    """Class to check and manage API specifications."""

    def __init__(self, spec_url: str) -> None:
        """Initialize with the URL of the API specification.

        Args:
            spec_url: URL to the OpenAPI specification
        """
        self.spec_url = spec_url

    def fetch_remote_spec(self) -> ApiSpecificationDTO:
        """Fetch the remote API specification.

        Returns:
            ApiSpecificationDTO: The parsed API specification

        Raises:
            httpx.HTTPError: If the request fails
        """
        logger.info(f"Fetching remote API specification from {self.spec_url}")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(self.spec_url)
            response.raise_for_status()
            spec_data = response.json()
        return ApiSpecificationDTO.model_validate(spec_data)

    def read_local_spec(self, file_path: str) -> ApiSpecificationDTO:
        """Read a local API specification file.

        Args:
            file_path: Path to the local specification file

        Returns:
            ApiSpecificationDTO: The parsed API specification

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        logger.info(f"Reading local API specification from {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            spec_data = json.load(f)
        return ApiSpecificationDTO.model_validate(spec_data)

    def save_spec(self, spec: ApiSpecificationDTO, file_path: str) -> None:
        """Save an API specification to a file.

        Args:
            spec: The API specification to save
            file_path: Path where to save the specification
        """
        logger.info(f"Saving API specification to {file_path}")
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(spec.model_dump(mode="json"), f, indent=2)


class ApiSpecChangeDetector:
    """Class to detect changes between API specifications."""

    def _compare_dicts(
        self,
        old_dict: Dict[str, Any],
        new_dict: Dict[str, Any],
        path: str = "",
    ) -> List[SpecificationDifference]:
        """Compare two dictionaries recursively and return differences.

        Args:
            old_dict: The old dictionary
            new_dict: The new dictionary
            path: Current path in the hierarchy (for reporting)

        Returns:
            List of differences between the dictionaries
        """
        differences = []

        # Check for removed keys
        for key in old_dict:
            if key not in new_dict:
                differences.append(
                    SpecificationDifference(
                        path=f"{path}.{key}" if path else key,
                        change_type=ChangeType.REMOVED,
                        old_value=old_dict[key],
                        new_value=None,
                    )
                )

        # Check for added or modified keys
        for key in new_dict:
            current_path = f"{path}.{key}" if path else key

            if key not in old_dict:
                differences.append(
                    SpecificationDifference(
                        path=current_path,
                        change_type=ChangeType.ADDED,
                        old_value=None,
                        new_value=new_dict[key],
                    )
                )
            else:
                # Key exists in both, check for differences
                old_value = old_dict[key]
                new_value = new_dict[key]

                # Different types
                if type(old_value) != type(new_value):
                    differences.append(
                        SpecificationDifference(
                            path=current_path,
                            change_type=ChangeType.MODIFIED,
                            old_value=old_value,
                            new_value=new_value,
                        )
                    )
                # Both are dictionaries, recurse
                elif isinstance(old_value, dict) and isinstance(new_value, dict):
                    differences.extend(self._compare_dicts(old_value, new_value, current_path))
                # Both are lists, compare items
                elif isinstance(old_value, list) and isinstance(new_value, list):
                    # Simple comparison for now
                    if old_value != new_value:
                        differences.append(
                            SpecificationDifference(
                                path=current_path,
                                change_type=ChangeType.MODIFIED,
                                old_value=old_value,
                                new_value=new_value,
                            )
                        )
                # Scalar values, direct comparison
                elif old_value != new_value:
                    differences.append(
                        SpecificationDifference(
                            path=current_path,
                            change_type=ChangeType.MODIFIED,
                            old_value=old_value,
                            new_value=new_value,
                        )
                    )

        return differences

    def compare_specs(
        self, old_spec: ApiSpecificationDTO, new_spec: ApiSpecificationDTO
    ) -> SpecificationComparisonResult:
        """Compare two API specifications and detect changes.

        Args:
            old_spec: The old API specification
            new_spec: The new API specification

        Returns:
            Result of the comparison with detected differences
        """
        logger.info("Comparing API specifications")

        # Convert specs to dictionaries for comparison
        old_dict = old_spec.model_dump(mode="json")
        new_dict = new_spec.model_dump(mode="json")

        # Find differences
        differences = self._compare_dicts(old_dict, new_dict)

        return SpecificationComparisonResult(
            has_changes=len(differences) > 0,
            differences=differences,
        )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Check for changes in the ClickUp API specification")
    parser.add_argument(
        "--spec-url",
        default="https://developer.clickup.com/openapi/673cf4cfdca96a0019533cad",
        help="URL to the ClickUp API specification",
    )
    parser.add_argument(
        "--local-spec",
        default="docs/api_spec/openapi.json",
        help="Path to the local API specification file",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update the local specification with the remote one",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    """Main function to check for API specification changes."""
    args = parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Initialize the checker
        checker = ApiSpecChecker(args.spec_url)

        # Fetch the remote specification
        remote_spec = checker.fetch_remote_spec()

        # Read the local specification
        try:
            local_spec = checker.read_local_spec(args.local_spec)
        except FileNotFoundError:
            logger.warning(f"Local specification file not found: {args.local_spec}")
            if args.update:
                logger.info("Creating local specification file")
                checker.save_spec(remote_spec, args.local_spec)
                return 0
            else:
                logger.error("Please provide a valid local specification file or use --update")
                return 1

        # Compare specifications
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(local_spec, remote_spec)

        if result.has_changes:
            logger.warning("API specification has changed!")
            logger.warning(f"Found {len(result.differences)} differences")

            # Print the differences
            for diff in result.differences:
                logger.warning(
                    f"{diff.change_type.upper()}: {diff.path}"
                    f"{f' - Old: {diff.old_value}' if diff.old_value is not None else ''}"
                    f"{f' - New: {diff.new_value}' if diff.new_value is not None else ''}"
                )

            if args.update:
                logger.info("Updating local specification file")
                checker.save_spec(remote_spec, args.local_spec)
                return 0
            else:
                logger.error("API specification has changed! Update the client and specification.")
                return 1
        else:
            logger.info("No changes detected in API specification")
            return 0

    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch remote API specification: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API specification: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
