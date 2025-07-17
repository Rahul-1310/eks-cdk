import os
from omegaconf import OmegaConf

def load_config():
    env = os.getenv("deployenv", "dev")
    config_path = f"conf/{env}-config.yaml"
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file: {config_path}")
    
    conf = OmegaConf.load(config_path)

    if not hasattr(conf, "environment") or not hasattr(conf.environment, "name"):
        raise ValueError("Config must contain 'environment.name'")
    
    return conf, env
