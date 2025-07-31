import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'gamewalking_config.ini'
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config['NETWORK'] = {
            'port': '9000',
            'buffer_size': '1024'
        }
        
        self.config['CONTROLS'] = {
            'forward_key': 'w',
            'step_duration': '0.1',
            'key_hold_duration': '0.05'
        }
        
        self.config['GENERAL'] = {
            'minimize_to_tray': 'true',
            'auto_start': 'false',
            'debug_mode': 'false'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
    
    def get(self, section, key, fallback=None):
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section, key, fallback=None):
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=None):
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()