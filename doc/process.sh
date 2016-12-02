#!/bin/sh
for f in `ls ./documentation/*.ipynb`; do
	jupyter nbconvert --to html $f 
done

mv ./documentation/*html ./documentation_html/

for f in `ls ./tutorials/*.ipynb`; do
	jupyter nbconvert --to html $f 
done

mv ./tutorials/*html ./tutorial_html/
