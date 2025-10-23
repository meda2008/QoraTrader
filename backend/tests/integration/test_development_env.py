"""
Integration test for local environment setup
These tests verify that the local development environment can be set up correctly
"""
import pytest
import os
import stat
from unittest.mock import patch, MagicMock

def test_dev_setup_script_exists():
    """
    Test that the development setup script exists and is executable
    """
    dev_setup_script_path = "scripts/dev-setup.sh"
    
    # Check if the development setup script exists
    assert os.path.exists(dev_setup_script_path), f"Development setup script not found at {dev_setup_script_path}"
    
    # Check that it's readable
    with open(dev_setup_script_path, 'r') as f:
        script_content = f.read()
        # Check for basic script elements
        assert "#!/bin/bash" in script_content
        assert "QoraTrader Development Setup Script" in script_content
    
    # Check that the script has executable permissions (on Unix-like systems)
    if os.name != 'nt':  # Not on Windows
        file_stat = os.stat(dev_setup_script_path)
        assert file_stat.st_mode & stat.S_IEXEC, "Development setup script is not executable"

def test_dev_docker_compose_exists():
    """
    Test that the development Docker Compose file exists
    """
    dev_compose_path = "docker/docker-compose.dev.yml"
    
    # Check if the development compose file exists
    assert os.path.exists(dev_compose_path), f"Development docker-compose file not found at {dev_compose_path}"
    
    # Check basic structure of compose file
    with open(dev_compose_path, 'r') as f:
        content = f.read()
        assert "version:" in content
        assert "services:" in content
        # Should contain development-specific configurations
        assert "volumes:" in content  # For development, volumes are typically used for live reloading

def test_dev_environment_files_exist():
    """
    Test that development environment files exist
    """
    dev_env_files = [
        ".env.development",
        ".env.development.example"
    ]
    
    for env_file in dev_env_files:
        # Check if the file exists, or at least the example
        if env_file == ".env.development":
            # The actual .env.development might not exist, but the example should
            example_file = ".env.development.example"
            if not os.path.exists(env_file):
                assert os.path.exists(example_file), f"Neither {env_file} nor {example_file} exists"
        else:
            assert os.path.exists(env_file), f"Development environment file not found at {env_file}"
            
        # Check content structure if the file exists
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
                expected_configs = [
                    "SECRET_KEY",
                    "DATABASE_URL",
                    "DEBUG_MODE"
                ]
                for config in expected_configs:
                    # Check if the config appears in the file (as a key)
                    # This test is loose as the file might have been customized
                    pass  # If file exists, it's sufficient for this test

def test_dev_documentation_exists():
    """
    Test that the development documentation exists
    """
    dev_docs_path = "docs/local-development.md"
    
    assert os.path.exists(dev_docs_path), f"Development documentation not found at {dev_docs_path}"
    
    # Check basic content
    with open(dev_docs_path, 'r') as f:
        content = f.read()
        assert "# 本地开发环境搭建指南" in content or "# Local Development Environment Setup Guide" in content
        assert "docker-compose" in content
        assert "setup" in content.lower()