"""
Configuration loader for MarkRender
Supports TOML configuration files
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


# Try to import tomllib (Python 3.11+) or fall back to tomli
try:
    import tomllib  # type: ignore
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


DEFAULT_CONFIG = {
    'theme': 'github-dark',
    'code_background': False,
    'line_numbers': True,
    'width': None,
    'force_color': False,
    'stream_code': True,
    'inline_code_color': None,
    'dim_mode': False,
}


class RendererConfig:
    """
    Configuration for MarkdownRenderer.
    Encapsulates all rendering settings.
    """
    def __init__(self, **kwargs):
        # Start with defaults
        self.config = DEFAULT_CONFIG.copy()
        
        # Merge with provided kwargs
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            elif hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None):
        """Create config from a file"""
        file_config = load_config(config_path)
        return cls(**file_config)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        raise AttributeError(f"'RendererConfig' object has no attribute '{name}'")


def find_config_file() -> Optional[Path]:
    """
    Find configuration file in standard locations.
    
    Search order:
    1. Current directory (.markrender.toml)
    2. Home directory (~/.markrender/config.toml)
    3. Home directory (~/.config/markrender/config.toml)
    
    Returns:
        Path to config file or None if not found
    """
    # Check current directory
    current_dir = Path.cwd()
    config_file = current_dir / '.markrender.toml'
    if config_file.exists():
        return config_file
    
    # Check home directory
    home = Path.home()
    config_file = home / '.markrender' / 'config.toml'
    if config_file.exists():
        return config_file
    
    # Check XDG config directory
    xdg_config = os.environ.get('XDG_CONFIG_HOME', home / '.config')
    config_file = Path(xdg_config) / 'markrender' / 'config.toml'
    if config_file.exists():
        return config_file
    
    return None


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to config file (default: find automatically)
        
    Returns:
        Configuration dictionary with defaults applied
    """
    if config_path is None:
        config_path = find_config_file()
    
    config = DEFAULT_CONFIG.copy()
    
    if config_path is None or tomllib is None:
        return config
    
    try:
        with open(config_path, 'rb') as f:
            file_config = tomllib.load(f)
        
        # Merge with defaults
        if 'rendering' in file_config:
            for key, value in file_config['rendering'].items():
                if key in config:
                    config[key] = value
        
        # Handle theme configuration
        if 'theme' in file_config:
            config['theme'] = file_config['theme']
        
        # Handle output configuration
        if 'output' in file_config:
            output_config = file_config['output']
            if 'width' in output_config:
                config['width'] = output_config['width']
            if 'force_color' in output_config:
                config['force_color'] = output_config['force_color']
        
        # Handle features configuration
        if 'features' in file_config:
            features_config = file_config['features']
            if 'stream_code' in features_config:
                config['stream_code'] = features_config['stream_code']
        
    except (IOError, OSError) as e:
        # Silently ignore file errors, use defaults
        pass
    except Exception as e:
        # Silently ignore parsing errors, use defaults
        pass
    
    return config


def create_default_config(config_path: Optional[Path] = None) -> Path:
    """
    Create a default configuration file.
    
    Args:
        config_path: Path to config file (default: ~/.markrender/config.toml)
        
    Returns:
        Path to created config file
    """
    if config_path is None:
        config_dir = Path.home() / '.markrender'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / 'config.toml'
    
    default_config_content = """# MarkRender Configuration
# See https://github.com/Praneeth-Gandodi/markrender for documentation

[theme]
name = "github-dark"

[rendering]
code_background = false
line_numbers = true

[output]
# width = 80  # Uncomment to set fixed width
force_color = false

[features]
stream_code = true
"""
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(default_config_content)
    
    return config_path


def get_config() -> Dict[str, Any]:
    """
    Get merged configuration from all sources.
    
    Returns:
        Configuration dictionary
    """
    return load_config()
