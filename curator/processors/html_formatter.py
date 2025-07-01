from bs4 import BeautifulSoup, NavigableString, Tag, Comment
from typing import List, Dict
from models.article import Article

class HTMLFormatter:
    
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

    def __handle_text_content(self, node: Tag) -> None:
        # text_content = node.get_text()
        # if text_content:
        #     p_wrapper = self._output.new_tag("div", attrs = {"class": "article-paragraph"})
        #     p = self._output.new_tag("p")
        #     p.string = text_content
        #     p_wrapper.append(p)
        #     self._section.append(p_wrapper)
        
        p_wrapper = self._output.new_tag("div", attrs = {"class": "article-paragraph"})
        p = self._output.new_tag("p")
        
        if isinstance(node, NavigableString):
            p.append(node.get_text())
        else:
            for child in node.children:
                if isinstance(child, Comment):
                    continue
                elif isinstance(child, Tag) and child.name == "br":
                    br = self._output.new_tag("br")
                    p.append(br)
                else:
                    child_text = child.get_text()
                    p.append(child_text)
                    
        p_wrapper.append(p)
        self._section.append(p_wrapper)
                    
    def __has_direct_text(self, node: Tag) -> bool:
        text_contents = list(filter(None, map(lambda s: s.strip(), node.find_all(string=True, recursive=False))))
        return bool(text_contents)
    
    def __handle_subheading(self, node: Tag) -> None:
        text_content = node.get_text(separator=" ", strip=True)
        if text_content:
            p_wrapper = self._output.new_tag("div", attrs = {"class": "article-subheading"})
            p = self._output.new_tag("h3")
            p.string = text_content
            p_wrapper.append(p)
            self._section.append(p_wrapper)
        
    # Traverse down the DOM tree
    def __recurse(self, node: Tag) -> None:
        # Handle Text
        if isinstance(node, NavigableString):
            self.__handle_text_content(node)
        
        if isinstance(node, Tag):
            if node.name in ["h1", "h2", "h3", "h4", "h5", "h6", "strong"]:
                self.__handle_subheading(node)
                    
            # If element has direct text content inside, grab all the text inside including the nested texts    
            elif self.__has_direct_text(node):
                self.__handle_text_content(node)
            
            else:
                # Otherwise, keep traversing down
                for child in node.children:
                    self.__recurse(child)
                    
    def __setup(self, article_source: str, article_title: str, article_published: str, article_url: str) -> None:
        self._output = BeautifulSoup("", "html.parser")
        # Create a <section class="article-container>"
        self._section = self._output.new_tag("section", attrs = {"class": "article-container"})
        
        # Create a <div> containing news source, article title, published date, and link to the original article
        article_header = self._output.new_tag("div", attrs = {"class": "article-header"})
        
        # Create a news source element and append it to header
        news_source = self._output.new_tag("p", attrs = {"id": "news-source"})
        news_source.string = article_source
        article_header.append(news_source)
        
        # Create a news title element and append it to header
        title = self._output.new_tag("h2", attrs = {"id": "article-title"})
        title.string = article_title
        article_header.append(title)
        
        # Create published date element and append it to header
        published = self._output.new_tag("p", attrs={"id": "date-published"})
        published.string = article_published
        article_header.append(published)
        
        # Create a original link element and append it to header
        original_link = self._output.new_tag("a", attrs = {"id": "original-link", "href": article_url})
        original_link.string = "기사 원문"
        article_header.append(original_link)
        
        self._section.append(article_header)
        self._output.append(self._section)
        
    def __add_img_section(self, article_image_url: str) -> None:
        if article_image_url:
            img_wrapper = self._output.new_tag("div", attrs = {"class": "article-image"})
            img_tag = self._output.new_tag("img", src = article_image_url)
            img_wrapper.append(img_tag)
            self._section.append(img_wrapper)
                
    def normalize(self, article: Article, idx) -> str:
        # Parse the input HTML structure
        original = BeautifulSoup(article.content, "html.parser")
        # Remove the unwanted elements beforehand
        self.__remove_elements(original)
        # Start the article format setup
        self.__setup(article.source, article.title, article.published_at, article.url)
        # Add image section right after header section
        self.__add_img_section(article.img_url)
        # Go down the DOM tree from input HTML
        for node in original.contents:
            self.__recurse(node)
        
        # FOR TESTING PURPOSES
        next_ = self._output.new_tag("a", attrs={"href": f"file:///Users/tonyha/Developer/crawler_test/results/naver/naver_{idx+1}.html"})
        next_.string = "다음"
        self._output.append(next_)
        
        # Return the final output
        return str(self._output)