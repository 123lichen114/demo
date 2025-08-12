from Util import *

class Config:
    def __init__(self,logger =None):
        self.json_template_path = "use_llm/output_json_template.json"
        self.prompt_style_path="use_llm/prompt_style.txt"
        self.logger = logger
       
    def get_prompt(self):
        json_template = read_json_as_string(self.json_template_path)
        try:
            with open(self.prompt_style_path, 'r', encoding='utf-8') as f:
                return f.read().format(json_template=json_template)
        except Exception as e:
            print(f"Error: {e}")
            return ""
if __name__ == "__main__":
    print(1)