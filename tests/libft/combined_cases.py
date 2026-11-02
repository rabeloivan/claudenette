"""Merged Francinette inputs; existing Claudenette cases win exact duplicates.

Input ideas: fsoares, Tripouille, Alelievr and War Machine. The oracles below
follow Libft 19.3; retired functions, exact malloc sizes and UB are excluded.
Detailed provenance/decisions: docs/FRANCINETTE_COVERAGE.md.
"""
import os

from tests.case_order import input_order, unique_cases
from utils.ui import display_str

SAMPLES = {
 'ft_strlen': [('',),('test basic !',),('the cake is a lie !',),('A'*4095,)],
 'ft_strdup': [('',),('sadfvbf',),('fdfjkdf\n35346',),('coucou',)],
 'ft_strchr': [(s,str(c)) for s,c in [('teste',ord('t')),('teste',ord('e')),('teste',0),
                 ('teste',ord('a')),('teste',ord('e')+256),('teste',1024)]] +
                [('éxé',str(c)) for c in (0,120,169,195,-87,425,451)],
 'ft_strrchr': [(s,str(c)) for s,c in [('teste',ord('e')),('teste',0),('xteste',ord('x')),
                  ('teste',ord('x')),('teste',1024+ord('e')),('teste',1024),('pepe y cparlos',ord('c'))]] +
                 [('éxé',str(c)) for c in (0,120,169,195,-87,425,451)],
 'ft_atoi': [(s,) for s in [' \t\v\n\r\f123','-1000043','    123','--123','-+123','+-123',
                '++123','- 123','+ 123','+\n123','1209','12/3','12;3',' +42lyon',
                '0'*128+'2147483647','-0002147483648', '+0000000000000000000000000000000000000000000000000000123',
                '546:5','-4886','+548','054854','000074','+-54','-+48','--47','++47',
                '+47+5','-47-5','\x1b475','\t\n\r\v\f  469 \n','\t\n\r\v\fd469 \n','\n\n\n  -46\b9 \n5d6']],
 'ft_strncmp': [(a,b,str(n)) for a,b in [('', ''),('test',''),('','test'),('teste','teste'),
                  ('teste','testex'),('teste','test'),('test','teste'),('Tripouille','TriPouille'),
                  ('Tripouille','TripouillE'),('Tripouille','TripouilleX')]
                 for n in (0,1,2,5,6,7,42,-1)],
 'ft_strnstr': [(h,n,str(size)) for h,n in [('', ''),('','teste'),('teste',''),
                ('abcdefgh','abc'),('abc','abcdef'),('aaxx','xx'),('aaabcabcd','aabc'),
                ('aaabcabcd','abcd'),('ababababac','ababac'),('MZIRIBMZIRIBMZP','MZIRIBMZP'),
                ('1','a'),('22','b')]
               for size in (0,1,2,3,4,5,8,9,-1)],
 'ft_substr': [(s,str(start),str(length)) for s in ('','hola') for start in (0,1,2,3,4,5,-1)
                for length in (0,1,2,3,4,5,30,-1)] +
               [('tripouille','0','42000'),('tripouille','100','1'),
                ('0123456789','9','10'),('BONJOUR LES HARICOTS !','8','14')],
 'ft_strjoin': [('', ''),('abc',''),('','abc'),('abcd','efghi'),('tripouille','42')],
 'ft_strtrim': [('', ''),('abcd',''),('','cdef'),(' . abcd',' '),('ab cd  f    ',' '),
              ('xxxz  test with x and z and x .  zx  xx z','z x'),('   abxfg  ','x'),
              ('.teste, bla ,.,.',',.'),('   xxxtripouille   xxx',' x'),('   xxx   xxx',' x'),
              ('abcdba','acb'),('   \t  \n\n \t\t  \n\n\nHello \t  Please\n Trim me !\n   \n \n \t\t\n  ',' \t\n')],
 'ft_split': [('hello!',' '),('xxxxxxxxhello!','x'),('hello!zzzzzzzz','z'),
             ('\t\t\t\thello!\t\t\t\t','\t'),('','a'),('ggggggggggg','g'),
             ('^^^1^^2a,^^^^3^^^^--h^^^^','^'),('nonempty',''),
             ('  tripouille  42  ',' '),('tripouille',''),('     ',' '),('chinimala',' '),
             ('1-2-3-4-5-42','-')],
 'ft_itoa': [(str(n),) for n in (0,1,-1,42,1000034,-10004,2147483647,-2147483648)] +
            [(str(sign*(10**power+delta)),) for power in range(1,10)
             for delta in (-1,0,1) for sign in (1,-1)],
 'ft_strmapi': [(s,mode) for s in ('','abcd0 ','abcdfsdfs','1234') for mode in ('add','zero')],
 'ft_striteri': [(s,mode) for s in ('','abcd0 ','abcdfsdfs','1234') for mode in ('add','zero')],
}


def _atoi(text):
    text=text.lstrip(' \t\n\r\f\v')
    sign=1
    if text[:1] in ('+','-'):
        sign=-1 if text[0]=='-' else 1
        text=text[1:]
    number=0
    for char in text:
        if not '0'<=char<='9': break
        number=number*10+ord(char)-48
    value=sign*number
    assert -2147483648<=value<=2147483647
    return str(value)


def _expected(function, args):
    if function=='ft_strlen': return str(len(args[0]))
    if function in ('ft_strdup','ft_itoa'): return args[0]
    if function=='ft_atoi': return _atoi(args[0])
    if function in ('ft_strchr','ft_strrchr'):
        char=bytes([int(args[1])%256])
        string=os.fsencode(args[0])+b'\0'
        position=string.find(char) if function=='ft_strchr' else string.rfind(char)
        return 'NULL' if position<0 else str(position)
    if function=='ft_strncmp':
        n=int(args[2]);n=2**64-1 if n<0 else n
        a,b=args[0][:n],args[1][:n]
        return '+' if a>b else '-' if a<b else '0'
    if function=='ft_strnstr':
        n=int(args[2]);n=2**64-1 if n<0 else n
        position=args[0][:n].find(args[1])
        return 'NULL' if position<0 else str(position)
    if function=='ft_substr':
        start=int(args[1])%(2**32);length=int(args[2])%(2**64)
        return '['+args[0][start:start+length]+']'
    if function=='ft_strjoin': return '['+''.join(args)+']'
    if function=='ft_strtrim':
        value=args[0].strip(args[1]) if args[1] else args[0]
        return '['+value+']'
    if function=='ft_split':
        words=[word for word in args[0].split(args[1]) if word] if args[1] else ([args[0]] if args[0] else [])
        return ''.join('['+word+']' for word in words)+'|'+str(len(words))
    if function in ('ft_strmapi','ft_striteri'):
        return ''.join(chr(ord(c)+i) if args[1]=='add' else '0' for i,c in enumerate(args[0]))
    raise KeyError(function)


def merge_cases(function, existing):
    added=[]
    for args in SAMPLES.get(function, []):
        args=list(args)
        added.append((args,None,_expected(function,args),
                      function+'('+', '.join(display_str(arg,limit=32) for arg in args)+')'))
    result=unique_cases(existing,added,key=lambda case:(case[0],case[1]))
    # Ordinary behavior first; unaligned/page/corpus campaigns run afterwards.
    def order(case):
        args=list(case[0])
        positions={'ft_itoa':(0,), 'ft_strchr':(1,), 'ft_strrchr':(1,),
                   'ft_strncmp':(2,), 'ft_strnstr':(2,), 'ft_substr':(1,2)}.get(function,())
        for index in positions:
            if index<len(args):
                value=int(args[index])
                args[index]=2**64-1 if value<0 and function in ('ft_substr','ft_strnstr','ft_strncmp') else value
        return input_order(args)
    return sorted(result,key=order)
