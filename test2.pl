PROGRAM add
CONST a:=1, b:=1;
VAR x, y;

BEGIN
    x:=1;
    y:=2;
    WHILE x<5 DO x:=x+1+1*1+3;
    IF y>0 THEN y:=-y-1;
    y:=y+x
END