if grep -r print "$PWD"/../sisl/*/*.py
then
    echo There should not be print statements with the SISL games
fi
if grep -r print "$PWD"/../gamma/*/*.py
then
    echo There should not be print statements with the gamma games
fi
