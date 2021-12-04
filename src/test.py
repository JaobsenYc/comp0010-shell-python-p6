Seq(
Pipe(
Call(
redirect:[RediectIn(*.py), RediectOut(out)], 
appName:call, 
args:['a', 'b', '"a"']
), 
Call(
redirect:[], 
appName:hello, 
args:[Subeval(echo arg), '*.py', '*s.py']
)
), 
Call(
redirect:[], 
appName:cat, 
args:['a']
)
)