#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_substr(char const *s, unsigned int start, size_t len);

size_t	ft_strlen(const char *s);

/* Linked against free_tracker.c. The result buffer therefore starts as 0xAA,
 * so a substr that copies the right bytes but never terminates runs past the
 * end instead of stopping at a lucky zero; and the 16-byte redzone fires if
 * it allocates len bytes rather than len + 1. */
int	main(int argc, char **argv)
{
	char	*out;

	if (argc != 4)
		return (1);
	out = ft_substr(argv[1], (unsigned int)atoi(argv[2]),
			(size_t)atoi(argv[3]));
	if (!out)
		return (write(1, "NULL", 4), 0);
	write(1, "[", 1);
	write(1, out, ft_strlen(out));
	write(1, "]", 1);
	h_check_redzones();
	return (0);
}
