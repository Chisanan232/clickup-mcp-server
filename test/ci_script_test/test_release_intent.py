"""Test the release intent parser script."""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

import jsonschema
import pytest
import yaml

from scripts.ci.release_intent import (
    ReleaseIntentError,
    get_defaults,
    get_workflow_dispatch_inputs,
    load_intent_file,
    load_schema,
    main,
    merge_intent_data,
    validate_intent,
    write_github_outputs,
)


class TestReleaseIntentError:
    """Test the custom ReleaseIntentError exception."""

    def test_exception_creation(self) -> None:
        """Test that ReleaseIntentError can be created with a message."""
        error_message = "Test error message"
        error = ReleaseIntentError(error_message)
        assert str(error) == error_message

    def test_exception_inheritance(self) -> None:
        """Test that ReleaseIntentError inherits from Exception."""
        error = ReleaseIntentError("test")
        assert isinstance(error, Exception)


class TestGetDefaults:
    """Test the get_defaults function."""

    def test_default_values(self) -> None:
        """Test that get_defaults returns expected default values."""
        defaults = get_defaults()
        
        expected_defaults = {
            'release': True,
            'level': 'auto',
            'artifacts': {
                'python': 'auto',
                'docker': 'auto',
                'docs': 'auto',
            },
            'notes': '',
        }
        
        assert defaults == expected_defaults

    def test_immutability(self) -> None:
        """Test that modifying returned defaults doesn't affect subsequent calls."""
        defaults1 = get_defaults()
        defaults1['release'] = False
        defaults1['artifacts']['python'] = 'skip'
        
        defaults2 = get_defaults()
        assert defaults2['release'] is True
        assert defaults2['artifacts']['python'] == 'auto'


class TestGetWorkflowDispatchInputs:
    """Test the get_workflow_dispatch_inputs function."""

    def test_no_environment_variables(self) -> None:
        """Test behavior when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            inputs = get_workflow_dispatch_inputs()
            
            expected = {
                'level': '',
                'python': '',
                'docker': '',
                'docs': '',
                'notes': '',
            }
            assert inputs == expected

    def test_with_environment_variables(self) -> None:
        """Test behavior when environment variables are set."""
        env_vars = {
            'INPUT_LEVEL': 'minor',
            'INPUT_PYTHON': 'force',
            'INPUT_DOCKER': 'skip',
            'INPUT_DOCS': 'auto',
            'INPUT_NOTES': 'Test release notes',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            inputs = get_workflow_dispatch_inputs()
            
            expected = {
                'level': 'minor',
                'python': 'force',
                'docker': 'skip',
                'docs': 'auto',
                'notes': 'Test release notes',
            }
            assert inputs == expected

    def test_whitespace_stripping(self) -> None:
        """Test that whitespace is stripped from environment variables."""
        env_vars = {
            'INPUT_LEVEL': '  patch  ',
            'INPUT_PYTHON': '\tforce\n',
            'INPUT_DOCKER': ' skip ',
            'INPUT_DOCS': 'auto\t',
            'INPUT_NOTES': '  Test notes  ',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            inputs = get_workflow_dispatch_inputs()
            
            expected = {
                'level': 'patch',
                'python': 'force',
                'docker': 'skip',
                'docs': 'auto',
                'notes': 'Test notes',
            }
            assert inputs == expected

    def test_partial_environment_variables(self) -> None:
        """Test behavior when only some environment variables are set."""
        env_vars = {
            'INPUT_LEVEL': 'major',
            'INPUT_NOTES': 'Partial test',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            inputs = get_workflow_dispatch_inputs()
            
            expected = {
                'level': 'major',
                'python': '',
                'docker': '',
                'docs': '',
                'notes': 'Partial test',
            }
            assert inputs == expected


class TestLoadSchema:
    """Test the load_schema function."""

    def test_load_valid_schema(self) -> None:
        """Test loading a valid JSON schema."""
        valid_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "release": {"type": "boolean"},
                "level": {"type": "string", "enum": ["auto", "patch", "minor", "major"]}
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(valid_schema))):
            with patch("pathlib.Path.exists", return_value=True):
                schema = load_schema()
                assert schema == valid_schema

    def test_schema_file_not_found(self) -> None:
        """Test behavior when schema file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(ReleaseIntentError, match="Schema file not found"):
                load_schema()

    def test_invalid_json_schema(self) -> None:
        """Test behavior when schema file contains invalid JSON."""
        invalid_json = "{ invalid json }"
        
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ReleaseIntentError, match="Failed to load schema"):
                    load_schema()

    def test_schema_file_read_error(self) -> None:
        """Test behavior when schema file cannot be read."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                with pytest.raises(ReleaseIntentError, match="Failed to load schema"):
                    load_schema()


class TestLoadIntentFile:
    """Test the load_intent_file function."""

    def test_load_valid_intent_file(self) -> None:
        """Test loading a valid intent YAML file."""
        valid_intent = {
            'release': True,
            'level': 'minor',
            'artifacts': {
                'python': 'auto',
                'docker': 'force',
                'docs': 'auto'
            },
            'notes': 'Test release'
        }
        
        yaml_content = yaml.dump(valid_intent)
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("pathlib.Path.exists", return_value=True):
                intent = load_intent_file()
                assert intent == valid_intent

    def test_intent_file_not_found(self) -> None:
        """Test behavior when intent file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            intent = load_intent_file()
            assert intent is None

    def test_invalid_yaml_intent_file(self) -> None:
        """Test behavior when intent file contains invalid YAML."""
        invalid_yaml = "{ invalid: yaml: content }"
        
        with patch("builtins.open", mock_open(read_data=invalid_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(ReleaseIntentError, match="Failed to load intent file"):
                    load_intent_file()

    def test_intent_file_read_error(self) -> None:
        """Test behavior when intent file cannot be read."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                with pytest.raises(ReleaseIntentError, match="Failed to load intent file"):
                    load_intent_file()

    def test_empty_intent_file(self) -> None:
        """Test behavior when intent file is empty."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("pathlib.Path.exists", return_value=True):
                intent = load_intent_file()
                assert intent is None


class TestMergeIntentData:
    """Test the merge_intent_data function."""

    def test_merge_defaults_only(self) -> None:
        """Test merging with only defaults (no file data or workflow inputs)."""
        defaults = get_defaults()
        file_data = None
        workflow_inputs = {
            'level': '',
            'python': '',
            'docker': '',
            'docs': '',
            'notes': '',
        }
        
        merged = merge_intent_data(defaults, file_data, workflow_inputs)
        assert merged == defaults

    def test_merge_with_file_data(self) -> None:
        """Test merging defaults with file data."""
        defaults = get_defaults()
        file_data = {
            'release': False,
            'level': 'major',
            'artifacts': {
                'python': 'skip',
                'docker': 'force'
            },
            'notes': 'File notes'
        }
        workflow_inputs = {
            'level': '',
            'python': '',
            'docker': '',
            'docs': '',
            'notes': '',
        }
        
        merged = merge_intent_data(defaults, file_data, workflow_inputs)
        
        expected = {
            'release': False,
            'level': 'major',
            'artifacts': {
                'python': 'skip',
                'docker': 'force',
                'docs': 'auto',  # From defaults
            },
            'notes': 'File notes'
        }
        assert merged == expected

    def test_merge_with_workflow_inputs(self) -> None:
        """Test merging with workflow dispatch inputs (highest priority)."""
        defaults = get_defaults()
        file_data = {
            'level': 'minor',
            'artifacts': {
                'python': 'auto',
                'docker': 'skip'
            },
            'notes': 'File notes'
        }
        workflow_inputs = {
            'level': 'patch',
            'python': 'force',
            'docker': '',
            'docs': 'skip',
            'notes': 'Workflow notes',
        }
        
        merged = merge_intent_data(defaults, file_data, workflow_inputs)
        
        expected = {
            'release': True,  # From defaults
            'level': 'patch',  # From workflow inputs (overrides file)
            'artifacts': {
                'python': 'force',  # From workflow inputs (overrides file)
                'docker': 'skip',   # From file (workflow input is empty)
                'docs': 'skip',     # From workflow inputs (overrides defaults)
            },
            'notes': 'Workflow notes'  # From workflow inputs (overrides file)
        }
        assert merged == expected

    def test_merge_complete_override(self) -> None:
        """Test complete override scenario."""
        defaults = get_defaults()
        file_data = {
            'release': False,
            'level': 'minor',
            'artifacts': {
                'python': 'skip',
                'docker': 'auto',
                'docs': 'force'
            },
            'notes': 'File notes'
        }
        workflow_inputs = {
            'level': 'major',
            'python': 'force',
            'docker': 'skip',
            'docs': 'auto',
            'notes': 'Override notes',
        }
        
        merged = merge_intent_data(defaults, file_data, workflow_inputs)
        
        expected = {
            'release': False,  # From file
            'level': 'major',  # From workflow inputs
            'artifacts': {
                'python': 'force',  # From workflow inputs
                'docker': 'skip',   # From workflow inputs
                'docs': 'auto',     # From workflow inputs
            },
            'notes': 'Override notes'  # From workflow inputs
        }
        assert merged == expected

    def test_merge_with_none_file_data(self) -> None:
        """Test merging when file_data is None."""
        defaults = get_defaults()
        file_data = None
        workflow_inputs = {
            'level': 'patch',
            'python': '',
            'docker': 'force',
            'docs': '',
            'notes': 'Workflow only',
        }
        
        merged = merge_intent_data(defaults, file_data, workflow_inputs)
        
        expected = {
            'release': True,  # From defaults
            'level': 'patch',  # From workflow inputs
            'artifacts': {
                'python': 'auto',  # From defaults (workflow input empty)
                'docker': 'force', # From workflow inputs
                'docs': 'auto',    # From defaults (workflow input empty)
            },
            'notes': 'Workflow only'  # From workflow inputs
        }
        assert merged == expected


class TestValidateIntent:
    """Test the validate_intent function."""

    def test_valid_intent(self) -> None:
        """Test validation of a valid intent."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "release": {"type": "boolean"},
                "level": {"type": "string", "enum": ["auto", "patch", "minor", "major"]},
                "artifacts": {
                    "type": "object",
                    "properties": {
                        "python": {"type": "string", "enum": ["auto", "force", "skip"]},
                        "docker": {"type": "string", "enum": ["auto", "force", "skip"]},
                        "docs": {"type": "string", "enum": ["auto", "force", "skip"]}
                    }
                },
                "notes": {"type": "string"}
            }
        }
        
        valid_intent = {
            "release": True,
            "level": "minor",
            "artifacts": {
                "python": "auto",
                "docker": "force",
                "docs": "skip"
            },
            "notes": "Test release"
        }
        
        # Should not raise any exception
        validate_intent(valid_intent, schema)

    def test_invalid_intent_validation_error(self) -> None:
        """Test validation with invalid intent data."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "release": {"type": "boolean"},
                "level": {"type": "string", "enum": ["auto", "patch", "minor", "major"]}
            }
        }
        
        invalid_intent = {
            "release": "not_a_boolean",  # Invalid type
            "level": "invalid_level"     # Invalid enum value
        }
        
        with pytest.raises(ReleaseIntentError, match="Intent validation failed"):
            validate_intent(invalid_intent, schema)

    def test_invalid_schema_error(self) -> None:
        """Test validation with invalid schema."""
        invalid_schema = {
            "$schema": "invalid_schema_url",
            "type": "invalid_type"
        }
        
        intent = {"release": True}
        
        with pytest.raises(ReleaseIntentError, match="Schema validation failed"):
            validate_intent(intent, invalid_schema)


class TestWriteGithubOutputs:
    """Test the write_github_outputs function."""

    def test_write_outputs_with_github_output_env(self) -> None:
        """Test writing GitHub outputs when GITHUB_OUTPUT is set."""
        intent = {
            'release': True,
            'level': 'minor',
            'artifacts': {
                'python': 'auto',
                'docker': 'force',
                'docs': 'skip'
            },
            'notes': 'Test notes'
        }
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch.dict(os.environ, {'GITHUB_OUTPUT': temp_file_path}):
                write_github_outputs(intent)
            
            # Read the written content
            with open(temp_file_path, 'r') as f:
                content = f.read()
            
            expected_lines = [
                "do_release=true",
                "level=minor",
                "python=auto",
                "docker=force",
                "docs=skip",
                "notes=Test notes"
            ]
            
            for line in expected_lines:
                assert line in content
                
        finally:
            os.unlink(temp_file_path)

    def test_write_outputs_with_false_release(self) -> None:
        """Test writing GitHub outputs when release is False."""
        intent = {
            'release': False,
            'level': 'auto',
            'artifacts': {
                'python': 'skip',
                'docker': 'skip',
                'docs': 'skip'
            },
            'notes': ''
        }
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            with patch.dict(os.environ, {'GITHUB_OUTPUT': temp_file_path}):
                write_github_outputs(intent)
            
            with open(temp_file_path, 'r') as f:
                content = f.read()
            
            assert "do_release=false" in content
            assert "level=auto" in content
            assert "python=skip" in content
            assert "notes=" in content
                
        finally:
            os.unlink(temp_file_path)

    def test_write_outputs_no_github_output_env(self) -> None:
        """Test that function handles missing GITHUB_OUTPUT gracefully."""
        intent = get_defaults()
        
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise any exception
            write_github_outputs(intent)

    def test_write_outputs_file_error(self) -> None:
        """Test behavior when cannot write to GITHUB_OUTPUT file."""
        intent = get_defaults()
        
        with patch.dict(os.environ, {'GITHUB_OUTPUT': '/invalid/path/output'}):
            with pytest.raises(ReleaseIntentError, match="Failed to write GitHub outputs"):
                write_github_outputs(intent)


class TestMainFunction:
    """Test the main function."""

    def test_main_success_with_defaults(self) -> None:
        """Test main function success with default values."""
        # Mock all the required functions
        mock_schema = {"type": "object"}
        mock_intent = None  # No intent file
        
        with patch('scripts.ci.release_intent.load_schema', return_value=mock_schema):
            with patch('scripts.ci.release_intent.load_intent_file', return_value=mock_intent):
                with patch('scripts.ci.release_intent.get_workflow_dispatch_inputs', return_value={
                    'level': '', 'python': '', 'docker': '', 'docs': '', 'notes': ''
                }):
                    with patch('scripts.ci.release_intent.validate_intent'):
                        with patch('scripts.ci.release_intent.write_github_outputs'):
                            with patch('builtins.print') as mock_print:
                                result = main()
                                
                                assert result == 0
                                mock_print.assert_called_once()
                                # Check that JSON was printed
                                printed_args = mock_print.call_args[0][0]
                                parsed_json = json.loads(printed_args)
                                assert parsed_json['release'] is True
                                assert parsed_json['level'] == 'auto'

    def test_main_success_with_file_data(self) -> None:
        """Test main function success with intent file data."""
        mock_schema = {"type": "object"}
        mock_intent = {
            'release': False,
            'level': 'major',
            'notes': 'Custom notes'
        }
        
        with patch('scripts.ci.release_intent.load_schema', return_value=mock_schema):
            with patch('scripts.ci.release_intent.load_intent_file', return_value=mock_intent):
                with patch('scripts.ci.release_intent.get_workflow_dispatch_inputs', return_value={
                    'level': '', 'python': '', 'docker': '', 'docs': '', 'notes': ''
                }):
                    with patch('scripts.ci.release_intent.validate_intent'):
                        with patch('scripts.ci.release_intent.write_github_outputs'):
                            with patch('builtins.print') as mock_print:
                                result = main()
                                
                                assert result == 0
                                printed_args = mock_print.call_args[0][0]
                                parsed_json = json.loads(printed_args)
                                assert parsed_json['release'] is False
                                assert parsed_json['level'] == 'major'
                                assert parsed_json['notes'] == 'Custom notes'

    def test_main_release_intent_error(self) -> None:
        """Test main function with ReleaseIntentError."""
        with patch('scripts.ci.release_intent.load_schema', side_effect=ReleaseIntentError("Schema error")):
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 1
                mock_print.assert_called_once_with("Error: Schema error", file=mock.ANY)

    def test_main_unexpected_error(self) -> None:
        """Test main function with unexpected error."""
        with patch('scripts.ci.release_intent.load_schema', side_effect=RuntimeError("Unexpected error")):
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 1
                mock_print.assert_called_once_with("Unexpected error: Unexpected error", file=mock.ANY)

    def test_main_success_with_workflow_inputs(self) -> None:
        """Test main function with workflow dispatch inputs."""
        mock_schema = {"type": "object"}
        mock_intent = None
        mock_workflow_inputs = {
            'level': 'patch',
            'python': 'force',
            'docker': 'skip',
            'docs': 'auto',
            'notes': 'Workflow notes'
        }
        
        with patch('scripts.ci.release_intent.load_schema', return_value=mock_schema):
            with patch('scripts.ci.release_intent.load_intent_file', return_value=mock_intent):
                with patch('scripts.ci.release_intent.get_workflow_dispatch_inputs', return_value=mock_workflow_inputs):
                    with patch('scripts.ci.release_intent.validate_intent'):
                        with patch('scripts.ci.release_intent.write_github_outputs'):
                            with patch('builtins.print') as mock_print:
                                result = main()
                                
                                assert result == 0
                                printed_args = mock_print.call_args[0][0]
                                parsed_json = json.loads(printed_args)
                                assert parsed_json['level'] == 'patch'
                                assert parsed_json['artifacts']['python'] == 'force'
                                assert parsed_json['artifacts']['docker'] == 'skip'
                                assert parsed_json['artifacts']['docs'] == 'auto'
                                assert parsed_json['notes'] == 'Workflow notes'

    def test_main_validation_error(self) -> None:
        """Test main function with validation error."""
        mock_schema = {"type": "object"}
        mock_intent = {"release": "invalid"}  # Invalid data
        
        with patch('scripts.ci.release_intent.load_schema', return_value=mock_schema):
            with patch('scripts.ci.release_intent.load_intent_file', return_value=mock_intent):
                with patch('scripts.ci.release_intent.get_workflow_dispatch_inputs', return_value={
                    'level': '', 'python': '', 'docker': '', 'docs': '', 'notes': ''
                }):
                    with patch('scripts.ci.release_intent.validate_intent', 
                              side_effect=ReleaseIntentError("Validation failed")):
                        with patch('builtins.print') as mock_print:
                            result = main()
                            
                            assert result == 1
                            mock_print.assert_called_once_with("Error: Validation failed", file=mock.ANY)


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_full_workflow_with_real_files(self) -> None:
        """Test the complete workflow with real temporary files."""
        # Create temporary files for schema and intent
        schema_content = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "release": {"type": "boolean"},
                "level": {"type": "string", "enum": ["auto", "patch", "minor", "major"]},
                "artifacts": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "python": {"type": "string", "enum": ["auto", "force", "skip"]},
                        "docker": {"type": "string", "enum": ["auto", "force", "skip"]},
                        "docs": {"type": "string", "enum": ["auto", "force", "skip"]}
                    }
                },
                "notes": {"type": "string"}
            },
            "required": []
        }
        
        intent_content = {
            'release': True,
            'level': 'minor',
            'artifacts': {
                'python': 'auto',
                'docker': 'force',
                'docs': 'auto'
            },
            'notes': 'Integration test release'
        }
        
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            github_dir = Path(temp_dir) / '.github' / 'tag_and_release'
            github_dir.mkdir(parents=True)
            
            schema_file = github_dir / 'schema.json'
            intent_file = github_dir / 'intent.yaml'
            output_file = Path(temp_dir) / 'github_output'
            
            # Write test files
            with open(schema_file, 'w') as f:
                json.dump(schema_content, f)
            
            with open(intent_file, 'w') as f:
                yaml.dump(intent_content, f)
            
            # Change to temp directory and run main
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch.dict(os.environ, {'GITHUB_OUTPUT': str(output_file)}):
                    with patch('builtins.print') as mock_print:
                        result = main()
                
                # Verify success
                assert result == 0
                
                # Verify JSON output
                printed_json = json.loads(mock_print.call_args[0][0])
                assert printed_json['release'] is True
                assert printed_json['level'] == 'minor'
                assert printed_json['artifacts']['docker'] == 'force'
                assert printed_json['notes'] == 'Integration test release'
                
                # Verify GitHub outputs file
                with open(output_file, 'r') as f:
                    output_content = f.read()
                
                assert 'do_release=true' in output_content
                assert 'level=minor' in output_content
                assert 'docker=force' in output_content
                assert 'notes=Integration test release' in output_content
                
            finally:
                os.chdir(original_cwd)

    def test_workflow_without_intent_file(self) -> None:
        """Test workflow when intent.yaml doesn't exist (should use defaults)."""
        schema_content = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "release": {"type": "boolean"}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            github_dir = Path(temp_dir) / '.github' / 'tag_and_release'
            github_dir.mkdir(parents=True)
            
            schema_file = github_dir / 'schema.json'
            
            with open(schema_file, 'w') as f:
                json.dump(schema_content, f)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch('builtins.print') as mock_print:
                    result = main()
                
                assert result == 0
                
                # Should use defaults
                printed_json = json.loads(mock_print.call_args[0][0])
                defaults = get_defaults()
                assert printed_json == defaults
                
            finally:
                os.chdir(original_cwd)
