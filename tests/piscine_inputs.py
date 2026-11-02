"""Reviewed Francinette C00-C05 inputs, using Claudenette's stronger oracles.

Sources and exclusions: docs/FRANCINETTE_COVERAGE.md. No upstream UI/runtime.
"""
from tests.case_order import input_order, unique_cases

BASE62 = 'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210'
ADDITIONS = {
 ('C00','ex00'): [("ft_putchar: repeated calls across a newline", 'x\ny')],
 ('C00','ex04'): [(1,'P'),(-1,'N')],
 ('C00','ex07'): [(n,str(n)) for n in (10,-1,-123)],
 ('C01','ex00'): [(567,'42'),(234,'42')],
 ('C01','ex01'): [(567,'42'),(234,'42')],
 ('C01','ex02'): [(13,23),(-23,45)],
 ('C01','ex03'): [(123,10,'12 3'),(-123,15,'-8 -3')],
 ('C01','ex04'): [(123,10,'12 3'),(-123,15,'-8 -3')],
 ('C01','ex05'): ['hello','holla\noutro'],
 ('C01','ex06'): ['hel\nlo'],
 ('C01','ex07'): [list(range(1,11)),list(range(1,12))],
 ('C01','ex08'): [list(range(123,0,-1)),list(range(10,0,-1)),list(range(11,0,-1))],
 ('C02','ex00'): ['ab','abc'],
 ('C02','ex01'): [('abcd',0),('abcd',2),('ab',8)],
 ('C02','ex02'): ['abc','abcdasda1d'],
 ('C02','ex03'): ['123','1234567a89'],
 ('C02','ex04'): ['abz','ab{','ab`','asdasda..','asdasAa'],
 ('C02','ex05'): ['ABZ','AB@','AB[','ADASFJET..'],
 ('C02','ex06'): [''.join(chr(c) for c in range(32,127)), 'fs\ts'],
 ('C02','ex07'): ['abcd-fsdAfddsSS'],
 ('C02','ex08'): ['ABDSDF-sdfsdf,,sdfYU74rff;'],
 ('C02','ex09'): ['salut, comMent tu vas ? 42mots quarAnte-deux; cinquante+et+uN e.puntOs'],
 ('C02','ex10'): [('abcd',0),('abcd',1),('abcsssd',6),('ab',8),('abasdf',7)],
 ('C02','ex11'): ['Coucou\ntu vas bien ?', ''.join(chr(c) for c in range(1,256))],
 ('C02','ex12'): [list(range(n)) for n in range(30)] + [list(range(256))+[0]],
 ('C03','ex00'): [('abcadef','abcadef'),('abcadef','abcad'),('abcad','abcadtg')],
 ('C03','ex01'): [('xxxxxx','yyyyyy',n) for n in (0,1,20)] +
                   [(a,b,n) for a,b in [('abcadef','abcad'),('abcad','abcadtg')] for n in (5,6)],
 ('C03','ex02'): [('aaaa','xyz'),('aaaa','')],
 ('C03','ex03'): [('aaaa','xyz',n) for n in (0,2,3,4,5)],
 ('C03','ex04'): [('xxxxxxxx',''),('xyxyza','xyz'),('xyxyaza','xyz')],
 ('C03','ex05'): [('aaaa','xyz',n) for n in (0,2,3,4,5,6,20)] + [('aaaaaaa','xyqwerrturerettw',2)],
 ('C04','ex00'): ['sggdsdsg','asd\vsfg'],
 ('C04','ex01'): ['hola!\n','asd\vsfg'],
 ('C04','ex02'): [(n,str(n)) for n in (10,-10)],
 ('C04','ex03'): ['\t\n\v\f\r      23','     ------+++++---12341',
                  '     ------+++++---123413','00000000002147483647','-2147483648','a'],
 ('C04','ex04'): [(n,'0123456789abcdef') for n in (42,-42,0,2147483647,-2147483648,-1)] +
                  [(2147483647,BASE62),(-2143247366,"'~"),(42,''),(42,'0'),
                   (42,'+-0123456789abcdef')],
 ('C04','ex05'): [('2a','0123456789abcdef'),('   --------+-2a','0123456789abcdef'),
                  ('   -+-2a','0123456789abcdef'),('   --------+- 2a','0123456789abcdef'),
                  ('   --------+-g','0123456789abcdef'),(' \v7fffffff','0123456789abcdef'),
                  (' \f-80000000','0123456789abcdef'),("-~~~~~~~~'~~~~~~'~'~~~'''''''~~'$","'~"),
                  ('Z'*150+'XEFnoY$',BASE62)] + [('2a',b) for b in ('','0','+-0','\t01')],
 ('C05','ex00'): [-10], ('C05','ex01'): [-10],
 ('C05','ex02'): [(1,-10),(1,-1),(10,0),(10,1),(10,2),(6,3)],
 ('C05','ex03'): [(1,-10),(1,-1),(10,0),(10,1),(10,2),(6,3)],
 ('C05','ex04'): [-20],
 ('C05','ex05'): [36,37,10000,10001,4000000,-36],
 ('C05','ex06'): [-1,-3,5,6,7,10,11,13,19,20],
 ('C05','ex07'): [-1,-3,3,5,6,7,10,11,13,19,20],
}


def extend_cases(module, exercise, cases):
    merged = unique_cases(cases, ADDITIONS.get((module,exercise), []))
    # Expected strings/descriptions are not part of input complexity.
    def payload(case):
        if module == 'C00' and exercise == 'ex00':
            return case[1]
        if (module,exercise) in {('C00','ex04'),('C00','ex07'),('C04','ex02'),
                                ('C01','ex00'),('C01','ex01')}:
            return case[0]
        if module == 'C01' and exercise in ('ex03','ex04'):
            return case[:2]
        return case
    return sorted(merged, key=lambda case: input_order(payload(case)))
