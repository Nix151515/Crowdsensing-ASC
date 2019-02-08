SRC=tema
TESTS=tests
OUT=out
STATS=stats

rm -f ${OUT} ${STATS}


time python -tt ${SRC}/tester.py -t test0 -o ${OUT} -i 1; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test1 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test2 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test3 -o ${OUT} -i 10; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test4 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test5 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test6 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test7 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -f ${TESTS}/test8 -o ${OUT} -i 5; echo
time python -tt ${SRC}/tester.py -t test9 -o ${OUT} -i 20; echo
time python -tt ${SRC}/tester.py -t test10 -o ${OUT} -i 20; echo

echo ""
echo "-----------------------------------------------------------------------"
echo ""

if [ -f ${OUT} ]
then
    cat ${OUT}
else
    echo "Tests failed"
fi
