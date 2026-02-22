from rich.console import Console as PreConsole
import os
from configparser import ConfigParser
import sys

class EmptyCommand(Exception):
    pass

class Console(PreConsole):
    def clear():
        os.system("cls")

class Config:
    def __init__(self, config_path: str):
        self.parser = ConfigParser()
        
        read_files = self.parser.read(config_path)
        if not read_files:
            raise FileNotFoundError("Config was not found")
    
    def get(self, section, value):
        return self.parser.get(section, value)
            
class ArgParser:
    def __init__(self, arg_array: list):
        self.valid = True
        
        self.args = arg_array.copy()
        self.args.pop(0)
        
        if len(self.args) == 0:
            raise EmptyCommand
        
        self.command = self.args[0]
        self.args.pop(0)
        
        self.params = [params for params in self.args if "-" not in params]
        self.flags = [flag for flag in self.args if "-" in flag]
        
    def get_details(self) -> tuple[str, list, list]:
        return self.command, self.params, self.flags

class Manager:
    def __init__(self, args: list):
        self.console = Console()
        self.config = Config("assets/config/config.cfg")
        
        try:
            self.arg_parser = ArgParser(args)
        except EmptyCommand:
            self.__raise(self.config.get("feedback", "no_command"))
        
        self.actions = self.__init_actions()
    
    def __raise(self, message):
        self.console.print(f"[red]Error[/red]: {message}")
        sys.exit()
        
    def __init_actions(self) -> dict:
        actions = {
            "list": {
                "description": "",
                "flag_index": [],
                "max_params": 0,
                "min_params": 0,
                "usage": "command [blue]list[/blue]",
                "function": self.__list
            }
        }
        
        return actions
    
    def __validate(self, func_name: str, params: list, flags:list):
        requirements = self.actions[func_name]
        
        max = requirements["max_params"]
        min = requirements["min_params"]
        
        if len(params) > max or len(params) < min: 
            self.__raise(self.config.get("feedback", "more_than_max"))
        
        flag_index = requirements["flag_index"]
        
        for flag in flags:
            if not flag in flag_index:
                self.__raise(self.config.get("feedback", "incorrect_flags"))
    
    def __list(self, params: list, flags: list):
        self.__validate("list", params, flags)
        
        for file in os.listdir(self.config.get("general", "scripts_path")):
            self.console.print(f"[yellow]{file.replace(".bat", "")}[/yellow]")
        
    
    def run(self):
        command, params, flags = self.arg_parser.get_details()
        
        if not command in self.actions:
            self.__raise(f"[blue]'{command}'[/blue]" + " " + self.config.get("feedback", "incorrect_command"))
        
        self.actions[command]["function"](params, flags)
    
        
        
        
        
                
                
        
        
