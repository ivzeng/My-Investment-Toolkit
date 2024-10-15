from ..helper.display import *

class BaseIO:
    def __init__(self) -> None:
        pass

    def input(self, content:str) -> str:
        pass

    def output(self, content:str) -> None:
        pass



class ConsoleIO:
    def __init__(self) -> None:
        pass

    def input(self, 
              content:str, indents: int = 0, width: int = None,
              pos: str = '<') -> str:
        return input(display(content, indents, width, pos))

    def input_item(self, content:str, t:type, default = None, exception = False,
                    indents: int = 0, width: int = None, pos: str = '<'):
        '''
        Gets input item; returns default if content = '' and returns exception
            if content cannot be converted to type t
        '''
        try:
            get = self.input(content, indents, width, pos)
            item = t(get)
        except:
            if get == '':
                return default
            else:
                return exception
        return item
    
    
    def output(self,
               content:str, indents: int = 0, width: int = None,
               pos: str = '<') -> None:
        print(display(content, indents, width, pos))
    
    def line_break(self) -> None:
        print()

    def output_message(self, message:str, type:None|str = None):
        if type is None:
            self.output(f'{message}')
        else:
            self.output(f'{type}: {message}')
    
    def output_error(self, message:str):
        self.output_message(message, 'Error')
    
    def output_warning(self, message:str):
        self.output_message(message, 'Warning')

    def output_hint(self, message:str):
        self.output_message(message, 'Hint')
