class ConvertedRule:
  def __init__(self, id, type, title, rule, status, severity):
    self.type = type
    self.id = id
    self.title = title
    self.rule = rule
    self.status = status
    self.severity = severity
  def __str__(self): 
    return f"| type: {self.type} | title: {self.title} | rule: {self.rule}"