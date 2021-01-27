import toml
from pathlib import Path

# read writehat config
config_file = Path(__file__).parent.parent / 'deploy/config.toml'
config = toml.load(str(config_file))