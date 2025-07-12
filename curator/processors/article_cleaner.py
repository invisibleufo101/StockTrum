from bs4 import BeautifulSoup
from parsel import Selector
from typing import Dict, List

class ArticleCleaner:
    
    def __init__(self, remove_selections: Dict[str, List] = {}):
        self.remove_selections = self.__format_remove_selections(remove_selections)
        self._output = None 
        self._section = None
        
    # Convert the original remove selections into valid CSS selectors for later tag removal
    def __format_remove_selections(self, selections: Dict[str, List]) -> List[str]:
        selection_lst = []
        for select_attr in selections:
            if select_attr == "class":
                for item in selections[select_attr]:
                    selection_lst.append(f".{item}") 
            elif select_attr == "id":
                for item in selections[select_attr]:
                    selection_lst.append(f"#{item}") 
            elif select_attr == "tag" or select_attr == "css":
                for item in selections[select_attr]:
                    selection_lst.append(item) 
            elif select_attr == "style":
                for item in selections[select_attr]:
                    selection_lst.append(f'[style*="{item}"]')
            else:
                for item in selections[select_attr]:
                    selection_lst.append(f'[{select_attr}="{item}"]')
        return selection_lst
                
    # Remove unwanted elements before reformatting
    def __remove_elements(self, original: BeautifulSoup) -> None:
        for selection in self.remove_selections:
            for element in original.select(selection):
                element.extract()
                
    def clean(self, html: str) -> str:
        # Remove the unwanted text from the input HTML string
        original = BeautifulSoup(html, "html.parser")
        self.__remove_elements(original)
        
        # Select only the text leftover
        selector = Selector(str(original))
        return selector.xpath("normalize-space(.)").get()
        
        
    
    