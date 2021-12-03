from abc import ABC, abstractmethod

class AST(ABC):
  @abstractmethod
  def accept(self, visitor):
    raise Exception("NotImplementedException")

class Substitution(AST):
  def __init__(self, quoted) -> None:
    self.quoted = quoted
  def accept(self, visitor):
    pass

  def __str__(self) -> str:
      return f"Subeval({str(self.quoted)})"

  def __repr__(self) -> str:
      return f"Subeval({str(self.quoted)})"

class RedirectIn(AST):
  def __init__(self, arg) -> None:
    self.arg = arg

  def accept(self, visitor):
    pass

  def __str__(self) -> str:
    return f"RediectIn({str(self.arg)})"

  def __repr__(self) -> str:
    return f"RediectIn({str(self.arg)})"
      
class RedirectOut(AST):
  def __init__(self, arg) -> None:
    self.arg = arg

  def accept(self, visitor):
    pass

  def __str__(self) -> str:
    return f"RediectOut({str(self.arg)})"

  def __repr__(self) -> str:
    return f"RediectOut({str(self.arg)})"

class Call(AST):
  def __init__(self, redirects, appName, args) -> None:
    self.redirects = redirects
    self.appName = appName
    self.args = args

  def accept(self, visitor):
    pass

  def __str__(self) -> str:
      return f"Call({str(self.redirects)}, {str(self.appName)}, {str(self.args)})"

class Seq(AST):
  def __init__(self, left, right) -> None:
    self.left = left
    self.right = right

  def accept(self, visitor):
    pass
  
  def __str__(self) -> str:
      return f"Seq({str(self.left)}, {str(self.right)})"

class Pipe(AST):
  def __init__(self, left, right) -> None:
    self.left = left
    self.right = right
  
  def accept(self, visitor):
    pass

  def __str__(self) -> str:
      return f"Pipe({str(self.left)}, {str(self.right)})"