@echo off

set SRC=tema
set TESTS=tests
set OUT=out
set STATS=stats

if exist %OUT% (
    del %OUT%
)

if exist %STATS% (
    del %STATS%
)

python -tt %SRC%/tester.py -t test0 -o %OUT% -i 1
python -tt %SRC%/tester.py -f %TESTS%/test1 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test2 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test3 -o %OUT% -i 10
python -tt %SRC%/tester.py -f %TESTS%/test4 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test5 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test6 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test7 -o %OUT% -i 5
python -tt %SRC%/tester.py -f %TESTS%/test8 -o %OUT% -i 5
python -tt %SRC%/tester.py -t test9 -o %OUT% -i 20
python -tt %SRC%/tester.py -t test10 -o %OUT% -i 20

echo ""
echo "-----------------------------------------------------------------------"
echo ""

if exist %OUT% (
    type %OUT%
) else (
    echo "Tests failed"
)

pause
