class ConvertedRule:
  def __init__(self, type, title, rule, status):
    self.type = type
    self.title = title
    self.rule = rule
    self.status = status
  def __str__(self): 
    return f"| type: {self.type} | title: {self.title} | rule: {self.rule}"