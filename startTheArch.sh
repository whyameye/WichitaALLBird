#!/bin/bash
xfce4-power-manager -q
xset -dpms
num=0
while [ 1 ]
      do
	  echo $num
	  python3 main.py $num
	  num=$((num + 1))
	  if (( num > 6 )); then
	      num=0
	  fi
done
