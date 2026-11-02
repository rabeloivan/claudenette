"""Read-only and guard-page cases shared only where the subject contracts match."""
from pathlib import Path
import tempfile
from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import print_test_pass, print_test_fail, print_exercise_result
from tests.libft.edge_cases import boundary_description

ROOT=Path(__file__).resolve().parent
KINDS={('C01','ft_strlen'):7,('C04','ft_strlen'):7,
 ('C02','ft_strcpy'):37,('C02','ft_strncpy'):38,('C02','ft_strlcpy'):11,
 ('C03','ft_strcmp'):42,('C03','ft_strncmp'):10,('C03','ft_strcat'):39,
 ('C03','ft_strncat'):41,('C03','ft_strstr'):40,('C03','ft_strlcat'):12}


def run_boundary_contracts(module,student_file):
    name=Path(student_file).stem
    kind=KINDS.get((module,name))
    if kind is None:return True
    inputs=[(0,0,0),(1,0,1),(7,1,0),(16,0,1),(31,7,0),(127,0,1),(257,31,0),(1024,0,1)]
    with tempfile.TemporaryDirectory(prefix='claudenette-boundaries-') as directory:
        exe=str(Path(directory)/'boundaries')
        flags=['-Wall','-Wextra','-Werror']
        wrapper=Path(directory)/'boundaries.c'
        wrapper.write_text(f'#define PISCINE\n#define KIND {kind}\n#define FT {name}\n'
                           +f'#include "{ROOT / "libft/edge_harness.c"}"\n')
        if not compile_source([str(Path(student_file).resolve()),str(wrapper),
                               str(ROOT/'free_tracker.c')],exe,flags=flags):return False
        passed=0
        for i,(length,offset,layout) in enumerate(inputs,1):
            actual,err,code=run_test_case(exe,args=[str(length),str(offset),str(layout)])
            description=boundary_description(name,kind,length,offset,layout)
            if code==0 and actual=='OK':
                passed+=1;print_test_pass(i,description)
            else:print_test_fail(i,description,expected='OK',actual=actual or err or f'exit {code}')
        print_exercise_result(name+' boundaries',passed,len(inputs))
        return passed==len(inputs)
