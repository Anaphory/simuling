#!/bin/sh

program=`which ${0}`
directory=`dirname ${program}`
beastlingini="${directory}/beastling.ini"
subsamplepy="${directory}/subsample.py"
consensuspy="${directory}/consensus.py"

while [ "!" -z $1 ]
do
    root=`basename $1 .tsv`
    echo $root/$root.xml
    python "${subsamplepy}" --vocabulary "$1" | beastling "${beastlingini}" -o $root/$root.xml
    (
        cd $root
        beast $root.xml
        python ${consensuspy} simulation.nex > $root/beast_$root.tre
    )
    shift
done
