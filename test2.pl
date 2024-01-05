PROGRAM add
VAR x, y;
BEGIN
    x:=1;
    y:=2;
    WHILE x<5 DO x:=x*(3+1)+(5+3);
    IF y>0 THEN y:=-y-1;
    y:=y+x
END