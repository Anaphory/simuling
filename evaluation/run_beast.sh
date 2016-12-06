#!/bin/sh

while [ "!" -z $1 ]
do
    echo $1
    root=`basename $1 .tsv`
    mkdir $root
    (
        echo "ID	Language_ID	Feature_ID	Form	Weight	Global_CogID	Value";
        tail -n +2 $1
    ) | sed -e 's/	/,/g'| beastling beastling.ini -o $root/$root.xml
    (
        cd $root
        beast $root.xml
    )
    shift
done
