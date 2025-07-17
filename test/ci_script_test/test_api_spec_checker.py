"""Test the ClickUp API specification change detector."""
import json
import os
from unittest import mock
from typing import Dict, Any

import pytest
from pydantic import BaseModel

# Path to our implementation that we'll create later
from scripts.ci.api_spec_checker import (
    ApiSpecChecker, 
    ApiSpecificationDTO, 
    ApiSpecChangeDetector,
    SpecificationDifference,
    SpecificationComparisonResult
)

class TestApiSpecificationDTO:
    """Tests for the API specification data transfer object."""
    
    def test_initialization(self) -> None:
        """Test that the DTO can be initialized from raw JSON data."""
        # Sample API spec (simplified)
        sample_spec = {
            "openapi": "3.1.0",
            "info": {
                "title": "ClickUp API v2 Reference",
                "version": "2.0"
            },
            "paths": {
                "/v2/user": {
                    "get": {
                        "summary": "Get Authorized User"
                    }
                }
            }
        }
        
        # Initialize from dictionary
        spec_dto = ApiSpecificationDTO.model_validate(sample_spec)
        
        # Verify initialization
        assert spec_dto.openapi == "3.1.0"
        assert spec_dto.info.title == "ClickUp API v2 Reference"
        assert spec_dto.info.version == "2.0"
        assert "/v2/user" in spec_dto.paths
    
    def test_equality(self) -> None:
        """Test that two identical DTOs are considered equal."""
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        assert spec1 == spec2
    
    def test_inequality(self) -> None:
        """Test that two different DTOs are considered not equal."""
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.1"},  # Different version
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        assert spec1 != spec2

class TestApiSpecChecker:
    """Tests for the API specification checker."""
    
    @mock.patch('requests.get')
    def test_fetch_remote_spec(self, mock_get: mock.MagicMock) -> None:
        """Test fetching the remote API specification."""
        # Setup mock response
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"}
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create checker and fetch spec
        checker = ApiSpecChecker("https://example.com/api/spec")
        spec = checker.fetch_remote_spec()
        
        # Assertions
        assert isinstance(spec, ApiSpecificationDTO)
        assert spec.info.title == "ClickUp API"
        mock_get.assert_called_once_with("https://example.com/api/spec")
    
    def test_read_local_spec(self) -> None:
        """Test reading a local API specification file."""
        # Create a temporary spec file
        temp_spec_path = "test_local_spec.json"
        sample_spec = {
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"}
        }
        
        try:
            with open(temp_spec_path, "w") as f:
                json.dump(sample_spec, f)
            
            # Create checker and read spec
            checker = ApiSpecChecker("https://example.com/api/spec")
            spec = checker.read_local_spec(temp_spec_path)
            
            # Assertions
            assert isinstance(spec, ApiSpecificationDTO)
            assert spec.info.title == "ClickUp API"
        finally:
            # Clean up
            if os.path.exists(temp_spec_path):
                os.remove(temp_spec_path)
    
    def test_save_spec(self) -> None:
        """Test saving an API specification to a file."""
        # Create a specification
        spec = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"}
        })
        
        # Save to temp file
        temp_save_path = "test_save_spec.json"
        try:
            checker = ApiSpecChecker("https://example.com/api/spec")
            checker.save_spec(spec, temp_save_path)
            
            # Verify file was created with correct content
            assert os.path.exists(temp_save_path)
            
            with open(temp_save_path, "r") as f:
                saved_spec = json.load(f)
                assert saved_spec["openapi"] == "3.1.0"
                assert saved_spec["info"]["title"] == "ClickUp API"
        finally:
            # Clean up
            if os.path.exists(temp_save_path):
                os.remove(temp_save_path)


class TestApiSpecChangeDetector:
    """Tests for the API specification change detector."""
    
    def test_detect_no_changes(self) -> None:
        """Test that no changes are detected when specs are identical."""
        # Create two identical specifications
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        # Detect changes
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(spec1, spec2)
        
        # Assertions
        assert result.has_changes is False
        assert len(result.differences) == 0
    
    def test_detect_version_change(self) -> None:
        """Test that a version change is detected."""
        # Create specifications with different versions
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.1"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        # Detect changes
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(spec1, spec2)
        
        # Assertions
        assert result.has_changes is True
        assert len(result.differences) == 1
        assert result.differences[0].path == "info.version"
        assert result.differences[0].old_value == "2.0"
        assert result.differences[0].new_value == "2.1"
    
    def test_detect_added_endpoint(self) -> None:
        """Test that an added endpoint is detected."""
        # Create specifications with different endpoints
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {
                "/test": {"get": {"summary": "Test"}},
                "/new": {"get": {"summary": "New Endpoint"}}
            }
        })
        
        # Detect changes
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(spec1, spec2)
        
        # Assertions
        assert result.has_changes is True
        assert len(result.differences) >= 1
        # Check for path addition
        path_added = any(
            diff.change_type == "added" and diff.path.startswith("paths./new")
            for diff in result.differences
        )
        assert path_added
    
    def test_detect_removed_endpoint(self) -> None:
        """Test that a removed endpoint is detected."""
        # Create specifications with different endpoints
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {
                "/test": {"get": {"summary": "Test"}},
                "/to_remove": {"get": {"summary": "Soon to be removed"}}
            }
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {"/test": {"get": {"summary": "Test"}}}
        })
        
        # Detect changes
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(spec1, spec2)
        
        # Assertions
        assert result.has_changes is True
        assert len(result.differences) >= 1
        # Check for path removal
        path_removed = any(
            diff.change_type == "removed" and diff.path.startswith("paths./to_remove")
            for diff in result.differences
        )
        assert path_removed

    def test_detect_modified_endpoint(self) -> None:
        """Test that a modified endpoint is detected."""
        # Create specifications with modified endpoint
        spec1 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {
                "/test": {"get": {"summary": "Test", "description": "Old description"}}
            }
        })
        
        spec2 = ApiSpecificationDTO.model_validate({
            "openapi": "3.1.0",
            "info": {"title": "ClickUp API", "version": "2.0"},
            "paths": {
                "/test": {"get": {"summary": "Test", "description": "Updated description"}}
            }
        })
        
        # Detect changes
        detector = ApiSpecChangeDetector()
        result = detector.compare_specs(spec1, spec2)
        
        # Assertions
        assert result.has_changes is True
        assert len(result.differences) >= 1
        # Check for path modification
        path_modified = any(
            diff.change_type == "modified" and 
            diff.path.startswith("paths./test.get.description") and
            diff.old_value == "Old description" and
            diff.new_value == "Updated description"
            for diff in result.differences
        )
        assert path_modified


class TestMainExecution:
    """Tests for the main execution flow."""
    
    @mock.patch('scripts.ci.api_spec_checker.ApiSpecChecker')
    @mock.patch('scripts.ci.api_spec_checker.ApiSpecChangeDetector')
    def test_main_no_changes(self, mock_detector_class: mock.MagicMock, mock_checker_class: mock.MagicMock) -> None:
        """Test the main execution when no changes are detected."""
        # Setup mocks
        mock_checker = mock.MagicMock()
        mock_detector = mock.MagicMock()
        
        mock_checker.fetch_remote_spec.return_value = "remote_spec"
        mock_checker.read_local_spec.return_value = "local_spec"
        
        mock_result = mock.MagicMock()
        mock_result.has_changes = False
        mock_detector.compare_specs.return_value = mock_result
        
        mock_checker_class.return_value = mock_checker
        mock_detector_class.return_value = mock_detector
        
        # Import the module to run the main function
        from scripts.ci.api_spec_checker import main
        
        # Run main with mocked environment
        with mock.patch('sys.argv', ['api_spec_checker.py', '--spec-url', 'https://example.com/spec', '--local-spec', 'local_spec.json']):
            # This should exit with 0
            assert main() == 0
        
        # Verify interactions
        mock_checker.fetch_remote_spec.assert_called_once()
        mock_checker.read_local_spec.assert_called_once()
        mock_detector.compare_specs.assert_called_once_with("local_spec", "remote_spec")
    
    @mock.patch('scripts.ci.api_spec_checker.ApiSpecChecker')
    @mock.patch('scripts.ci.api_spec_checker.ApiSpecChangeDetector')
    def test_main_with_changes(self, mock_detector_class: mock.MagicMock, mock_checker_class: mock.MagicMock) -> None:
        """Test the main execution when changes are detected."""
        # Setup mocks
        mock_checker = mock.MagicMock()
        mock_detector = mock.MagicMock()
        
        mock_checker.fetch_remote_spec.return_value = "remote_spec"
        mock_checker.read_local_spec.return_value = "local_spec"
        
        mock_result = mock.MagicMock()
        mock_result.has_changes = True
        mock_result.differences = [
            SpecificationDifference(
                path="info.version",
                change_type="modified",
                old_value="2.0",
                new_value="2.1"
            )
        ]
        mock_detector.compare_specs.return_value = mock_result
        
        mock_checker_class.return_value = mock_checker
        mock_detector_class.return_value = mock_detector
        
        # Import the module to run the main function
        from scripts.ci.api_spec_checker import main
        
        # Run main with mocked environment
        with mock.patch('sys.argv', ['api_spec_checker.py', '--spec-url', 'https://example.com/spec', '--local-spec', 'local_spec.json']):
            # This should exit with 1 due to detected changes
            assert main() == 1
        
        # Verify interactions
        mock_checker.fetch_remote_spec.assert_called_once()
        mock_checker.read_local_spec.assert_called_once()
        mock_detector.compare_specs.assert_called_once_with("local_spec", "remote_spec")
