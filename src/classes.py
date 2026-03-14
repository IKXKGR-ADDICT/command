from rich.console import Console as PreConsole
from rich.table import Table
import os
from configparser import ConfigParser
import sys
import shutil as su
from exceptions import EmptyCommand
from typing import Unpack, TypedDict, Callable
    
class Console(PreConsole):
    def clear(self):
        os.system("cls")
    
    def pad_print(self, renderable):
        "Normal print method but adds newlines after and before the string"
        
        self.print("")
        self.print(renderable)
        self.print("")

class Config:
    def __init__(self, config_path: str):
        self.__parser = ConfigParser()
        
        read_files = self.__parser.read(config_path)
        if not read_files:
            raise FileNotFoundError("Config was not found")
    
    def __call__(self, section:str, value:str):
        return self.__parser.get(section, value)
    
class ArgParser:
    def __init__(self, arg_array: list):
        self.__valid = True
        
        self.__args = arg_array.copy()
        self.__args.pop(0)
        
        if len(self.__args) == 0:
            raise EmptyCommand
        
        self.__command = self.__args[0]
        self.__args.pop(0)
        
        self.__params = [params for params in self.__args if "-" not in params]
        self.__flags = [flag for flag in self.__args if "-" in flag]
        
    def get_details(self) -> tuple[str, list, list]:
        return self.__command, self.__params, self.__flags

class CommandArguments(TypedDict):
    console: Console
    params: list
    flags: list
    
class Command:
    def __init__(self, name:str, usage:str, func: Callable, flag_index: dict = {}, max_params:int = 0, min_params:int = 0, description:str = ""):
        self.name = name
        self.usage = usage
        self.flag_index = flag_index
        self.max_params = max_params
        self.min_params = min_params
        self.description = description
        
        self.__func = func
    
    def __call__(self, params: list = [], flags: list = [], console: Console = None):
        self.__func(console = console, params = params, flags = flags)
    
class Manager:
    def __init__(self, args: list):
        self.__config = Config("assets/config/config.cfg")
        self.__console = Console()
        
        try:
            self.__arg_parser = ArgParser(args)
        except EmptyCommand:
            self.__invalid_command()
        
        self.__menu: dict[str, Command] = self.__build_menu()
    
    def __build_menu(self) -> dict[str, Command]:
        return {
            "help": Command(
                name="help",
                usage="help",
                func=self.__help,
                description="Shows a list of all commands available and their parameters"
            ),
            "list": Command(
                name="list",
                usage="list",
                func=self.__list,
                description="Shows a list of all custom user scripts installed on this computer"
            )
        }
    
    def __invalid_command(self):
        self.__console.pad_print(self.__config("feedback", "no_command"))
    
    def __build_generic_table(self) -> Table:
        table = Table(box=None, show_header=False)
        table.add_column("field1")
        
        return table
        
    def __build_help_table(self) -> Table:
        table = Table(box=None, show_header=False)
        
        table.add_column("name")
        table.add_column ("description")
        
        for command in self.__menu.values():
            table.add_row(self.__color(command.name, "yellow"), command.description)
        
        return table
    
    def __color(self, string: str, color: str = ""):
        return f"[{color}]{string}[/{color}]"

    def __list(self, **arguments: Unpack[CommandArguments]):
        table = self.__build_generic_table()
        console = arguments["console"]
        
        for file in os.listdir(self.__config("general", "scripts_path")):
            table.add_row(self.__color(file.replace(".bat", ""), "yellow"))
        
        console.pad_print(table)

    def __help(self, **arguments: Unpack[CommandArguments]):
        console = arguments["console"]
        
        console.pad_print(self.__build_help_table())
    
    def run(self):
        command, params, flags = self.__arg_parser.get_details()
    
        try:
            self.__menu[command](console=self.__console, params=params, flags=flags)
        except KeyError:
            self.__console.pad_print(self.__config("feedback", "incorrect_command"))