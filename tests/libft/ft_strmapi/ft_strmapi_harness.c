#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_strmapi(char const *s, char (*f)(unsigned int, char));

size_t	ft_strlen(const char *s);

/* f depends on BOTH arguments: the index decides the case, the character
 * supplies the letter. A student who passes only the character (or only the
 * index) produces a different string, which a case-insensitive or
 * index-ignoring f would have hidden. */
static int mode;

static char	alternate_case(unsigned int i, char c)
{
	if (mode == 1) return ((char)(c + i));
	if (mode == 2) return ('0');
	if (i % 2 == 0)
	{
		if (c >= 'a' && c <= 'z')
			return (c - 32);
		return (c);
	}
	if (c >= 'A' && c <= 'Z')
		return (c + 32);
	return (c);
}

/* Linked against free_tracker.c, so the result buffer starts poisoned: a
 * strmapi that maps every character but never writes the terminator runs on
 * into 0xAA rather than stopping at a conveniently zeroed byte. */
int	main(int argc, char **argv)
{
	char	*out;

	if (argc < 2 || argc > 3)
		return (1);
	mode = argc == 3 ? (argv[2][0] == 'a' ? 1 : 2) : 0;
	out = ft_strmapi(argv[1], alternate_case);
	if (!out)
		return (write(1, "NULL", 4), 0);
	if (out == argv[1])
		return (write(1, "SAMEPTR", 7), 0);
	write(1, out, ft_strlen(out));
	h_check_redzones();
	return (0);
}
