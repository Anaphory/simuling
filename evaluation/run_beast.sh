#!/bin/sh

program=`which ${0}`
directory=`dirname ${program}`
beastlingini="$directory/beastling.ini"

while [ "!" -z $1 ]
do
    root=`basename $1 .tsv`
    echo $root/$root.xml
    mkdir -p $root
    (
        echo "ID	Language_ID	Feature_ID	Form	Weight	Global_CogID	Value";
        tail -n +2 $1
    ) | sed -e 's/	/,/g' | beastling "${beastlingini}" -o $root/$root.xml
    cd $root
    beast $root.xml
    shift
done
