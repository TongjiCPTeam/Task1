PROGRAM add
VAR x,y;
BEGIN
  x:=1;
  y:=2;
  WHILE x<5 DO x:=x+1;
  IF y>0 THEN y:=y-1;
  y:=y+x;
END.