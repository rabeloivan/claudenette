"""Deterministic edge campaigns replacing overlapping weaker upstream checks."""
from pathlib import Path

FUNCTIONS = ['ft_memset','ft_bzero','ft_memcpy','ft_memmove','ft_memchr','ft_memcmp',
 'ft_strlen','ft_strchr','ft_strrchr','ft_strncmp','ft_strlcpy','ft_strlcat','ft_strnstr',
 'ft_strdup','ft_strmapi','ft_striteri','ft_lstnew','ft_lstadd_front','ft_lstadd_back',
 'ft_lstsize','ft_lstlast','ft_lstdelone','ft_lstclear','ft_lstiter','ft_lstmap',
 'ft_putchar_fd','ft_putstr_fd','ft_putendl_fd','ft_putnbr_fd']
COVERED_EXISTING={'ft_isalpha','ft_isdigit','ft_isalnum','ft_isascii','ft_isprint','ft_toupper','ft_tolower'}
KINDS = {name:i+1 for i,name in enumerate(FUNCTIONS)}
KINDS.update({'ft_itoa':43,'ft_calloc':44,'ft_substr':45,'ft_strjoin':46,
              'ft_strtrim':47,'ft_split':48,'ft_atoi':49})
HARNESS = str(Path(__file__).with_name('edge_harness.c'))


def boundary_description(function, kind, length, offset, layout):
    """Describe the checked behavior, not the guard-page implementation."""
    position = ("at buffer end" if layout else
                f"starting {offset} {'byte' if offset == 1 else 'bytes'} into buffer" if offset else
                "at buffer start")
    if kind == 7:
        return f'{function}({length}-byte string {position}) output {length}'
    checks = {
        1: 'fills only the requested bytes', 2: 'zeros only the requested bytes',
        3: 'copies every byte and leaves surrounding memory unchanged',
        4: 'copies correctly even when source and destination overlap',
        5: 'finds the first matching byte, including values above 127',
        6: 'compares bytes correctly, including values above 127',
        8: 'finds the first character or the ending zero byte',
        9: 'finds the last character or the ending zero byte',
        10: 'compares up to the limit and stops at the ending zero byte',
        11: 'handles small buffers and returns the full source length',
        12: 'handles full buffers without reading or writing past the limit',
        13: 'finds the first substring within the requested limit',
        14: 'returns a separate copy that can be freed',
        37: 'copies the string and its ending zero byte',
        38: 'respects the copy limit and fills unused space with zero bytes',
        39: 'appends the string without changing surrounding memory',
        40: 'finds the first substring, including an empty search',
        41: 'appends at most the requested number of bytes',
        42: 'compares strings correctly, including byte values above 127',
    }
    unit = 'byte' if length == 1 else 'bytes'
    return f'{function}({length} {unit} {position}): {checks[kind]}'


def cases_for(function):
    kind=KINDS.get(function)
    if not kind: return []
    if kind==49:
        inputs=[(0,0,0,'handles every possible first byte, spaces and the first digit')]
    elif kind>=45:
        checks={45:'clamps the start and length to the input',
                46:'joins strings, including two references to the same input',
                47:'trims only matching bytes at the beginning and end',
                48:'splits into separate words and ends the array with NULL'}
        inputs=[(n,0,1,f'{n}-byte read-only input: {checks[kind]}; result can be freed')
                for n in (0,1,17,257,1024)]
    elif kind in (43,44):
        inputs=([(0,0,0,'formats zero, negative numbers and int limits'),
                 (1024,0,0,'formats 1,024 additional integers and checks every digit')]
                if kind==43 else
                [(0,0,0,'handles zero-sized requests and rejects size overflow'),
                 (1024,0,0,'zeros every byte in larger allocations and returns freeable memory')])
    elif kind>=26:
        # These two C campaigns ignore length: running 0 and 127 repeats
        # exactly the same calls, byte values and assertions.
        if kind==26:
            inputs=[(0,0,0,'writes all 256 byte values to an opened file')]
        elif kind==29:
            inputs=[(0,0,0,'writes zero, negative numbers and int limits to an opened file')]
        else:
            ending=' and a newline each time' if kind==28 else ''
            inputs=[(n,0,0,f'writes a {n}-byte string three times{ending} to the same file')
                    for n in (0,127)]
    elif kind==17:
        # lstnew receives NULL or &values[0]; the list length and content
        # layout previously varied unrelated setup, not the tested argument.
        inputs=[(0,0,0,'creates a separately allocated node with NULL content and next = NULL'),
                (1,0,0,'stores the original integer pointer in a new node with next = NULL')]
    elif kind>=17:
        checks={18:'prepends the new node and keeps the existing links',
                19:'appends the new chain and preserves its links',
                20:'returns the exact number of nodes',
                21:'returns the original last node, or NULL for an empty list',
                22:'frees only the selected node and calls del once',
                23:'frees all nodes, calls del for each content and sets the head to NULL',
                24:'calls the callback once per node, in list order',
                25:'creates independent nodes and preserves the source list'}
        # A zero-node list has no content layout. lstdelone's empty-list
        # branch never calls the student function; the NULL probe covers it.
        lengths=(1,2,17,257) if kind==22 else (0,1,2,17,257)
        inputs=[(n,0,layout,f'{n}-node list'+(' with NULL contents' if layout else '')+
                 f': {checks[kind]}')
                for n in lengths for layout in ((0,1) if n else (0,))]
    elif kind>=15:
        callbacks=('index-based callback', 'zero-byte callback', 'constant-result callback')
        inputs=[(n,0,layout,
                 f'empty string; no calls to the {callbacks[layout]}' if not n else
                 f'{n}-character string; '+
                 ('passes each character and its index to the callback' if not layout else
                  'visits every original character even when the callback produces a zero byte' if layout==1 else
                  'accepts the same callback result for every character'))
                for n in (0,1,17,257) for layout in range(3)]
    else:
        inputs=[(n,off,layout,boundary_description(function,kind,n,off,layout))
                for n,off,layout in ([(0,0,0),(1,0,1),(7,1,0),(16,0,1),(31,7,0)] +
                                    [(63,offset,0) for offset in range(8)] +
                                    [(127,0,1),(257,31,0),(1024,0,1),(65536,0,1)])]
    cases = [([str(n),str(off),str(layout)],None,'OK',
              description if description.startswith(function+'(') else function+': '+description)
             for n,off,layout,description in inputs]
    if kind in (1,2,3,4):
        size=128*1024*1024 if kind==4 else 0xF0000
        cases.append(([str(size),'0','2'],None,'OK',function+f': checks every byte in a {size:,}-byte buffer',None,20))
    return cases
