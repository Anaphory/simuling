# This test is an attempt to test for a couple of features
# To allow for quick removal of created files, all files are prefixed by LP_ 
# First, we create one random tree using the normal commands

python3 maketrees/make_trees.py -t 1 --tree-file=LP_random.tre

# Now we create the languages, using the network.gml file in graph/

python3 -m phylo --semantic-network=graph/network.gml LP_random.tre

# Now we carry out a couple of different analyses, checking for different settings
# - switch the etyma flag on and off
# - search in two sublists: Swadesh-1955-100 and Swadesh-1952-200
# - switch tree_calc (neighbor, upgma)

## all with etyma=true
# first, full list 
python3 evaluation/lingpy-analysis.py LP_random-1.tsv -m neighbor -s etyma > LP_et-nj-s0.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv -m upgma -s etyma > LP_et-up-s0.tre

# next sublist 1
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1955-100 -m neighbor -s etyma > LP_et-nj-s1.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1955-100 -m upgma -s etyma > LP_et-up-s1.tre

# next sublist 2
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1952-200 -m neighbor -s etyma > LP_et-nj-s2.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1952-200 -m upgma -s etyma > LP_et-up-s2.tre

## all with etyma=false
# first, full list 
python3 evaluation/lingpy-analysis.py LP_random-1.tsv -m neighbor -s false > LP_nt-nj-s0.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv -m upgma -s false > LP_nt-up-s0.tre

# next sublist 1
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1955-100 -m neighbor -s false > LP_nt-nj-s1.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1955-100 -m upgma -s false > LP_nt-up-s1.tre

# next sublist 2
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1952-200 -m neighbor -s false > LP_nt-nj-s2.tre
python3 evaluation/lingpy-analysis.py LP_random-1.tsv --sublist --sublistname=Swadesh-1952-200 -m upgma -s false > LP_nt-up-s2.tre



# analysis
echo ETYMA NJOIN ---- `python3 evaluation/distance.py LP_random.tre LP_et-nj-s0.tre`
echo ETYMA UPGMA ---- `python3 evaluation/distance.py LP_random.tre LP_et-up-s0.tre`
echo ETYMA NJOIN Swa1 `python3 evaluation/distance.py LP_random.tre LP_et-nj-s1.tre`
echo ETYMA UPGMA Swa1 `python3 evaluation/distance.py LP_random.tre LP_et-up-s1.tre`
echo ETYMA NJOIN Swa2 `python3 evaluation/distance.py LP_random.tre LP_et-nj-s2.tre`
echo ETYMA UPGMA Swa2 `python3 evaluation/distance.py LP_random.tre LP_et-up-s2.tre`
echo ----- NJOIN ---- `python3 evaluation/distance.py LP_random.tre LP_nt-nj-s0.tre`
echo ----- UPGMA ---- `python3 evaluation/distance.py LP_random.tre LP_nt-up-s0.tre`
echo ----- NJOIN Swa1 `python3 evaluation/distance.py LP_random.tre LP_nt-nj-s1.tre`
echo ----- UPGMA Swa1 `python3 evaluation/distance.py LP_random.tre LP_nt-up-s1.tre`
echo ----- NJOIN Swa2 `python3 evaluation/distance.py LP_random.tre LP_nt-nj-s2.tre`
echo ----- UPGMA Swa2 `python3 evaluation/distance.py LP_random.tre LP_nt-up-s2.tre`

