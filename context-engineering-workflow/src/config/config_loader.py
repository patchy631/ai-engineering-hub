import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Utility class for loading YAML configuration files"""
    
    def __init__(self, config_root: Optional[str] = None):
        if config_root is None:
            project_root = Path(__file__).parent.parent.parent
            self.config_root = project_root / "config"
        else:
            self.config_root = Path(config_root)
    
    def load_agents_config(self, config_file: str = "research_agents.yaml") -> Dict[str, Any]:
        """Load agents configuration from YAML file"""
        config_path = self.config_root / "agents" / config_file
        return self._load_yaml_file(config_path)
    
    def load_tasks_config(self, config_file: str = "research_tasks.yaml") -> Dict[str, Any]:
        """Load tasks configuration from YAML file"""
        config_path = self.config_root / "tasks" / config_file
        return self._load_yaml_file(config_path)
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML file and return its contents"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                
            if content is None:
                raise ValueError(f"Empty or invalid YAML file: {file_path}")
                
            return content
            
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            raise Exception(f"Error loading configuration file {file_path}: {e}")
    
    def get_agent_config(self, agent_name: str, config_file: str = "research_agents.yaml") -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        agents_config = self.load_agents_config(config_file)
        
        if agent_name not in agents_config:
            raise KeyError(f"Agent '{agent_name}' not found in configuration file")
        
        return agents_config[agent_name]
    
    def get_task_config(self, task_name: str, config_file: str = "research_tasks.yaml") -> Dict[str, Any]:
        """Get configuration for a specific task"""
        tasks_config = self.load_tasks_config(config_file)
        
        if task_name not in tasks_config:
            raise KeyError(f"Task '{task_name}' not found in configuration file")
        
        return tasks_config[task_name]
