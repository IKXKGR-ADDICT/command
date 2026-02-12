import sys
from rich.console import Console as PreConsole
from rich.prompt import Prompt
import os
from configparser import ConfigParser

class Console(PreConsole):
    def clear(self):
        os.system("cls")

class Config():
    def __init__(self):
        self.config = ConfigParser()
        read_files = self.config.read("assets/config/config.cfg")
        
        if not read_files:
            raise FileNotFoundError("Config was not found.")
    
    def get_config(self):
        return self.config

class ArgParser:
    def __init__(self, args: list):
        self.args = args
        self.args.pop(0)
        
        self.flags = self.__catch_flags()
        
        self.command = self.args[0]
        self.args.pop(0)
    
    def __catch_flags(self):
        flags = []
        
        for arg in self.args:
            if "-" in arg:
                flags.append(arg)
                self.args.pop(self.args.index(arg))
        
        return flags
    
    def get_args(self) -> tuple[str, list, list]:
        return (self.command, self.args, self.flags)
    
class Manager:
    def __init__(self, args):
        self.arg_parser = ArgParser(args)
        self.console = Console()
        self.config = Config()
        
        self.actions = self.__actions()
    
    def __actions(self):
        actions = {
            "list": {
                "description": "List all available user-made commands",
                "function": self.__list
            }
        }
        
        return actions

    def __list(self, *void):
        for script in os.listdir(self.config.get_config().get("general", "scripts_path")):
            self.console.print(f"[yellow]{script.replace(".bat", "")}[/yellow]")
        
    def run(self):
        args = self.arg_parser.get_args()
        
        command = args[0].lower().strip()
        params = args[1]
        flags = args[2]
        
        self.actions[command]["function"](params)