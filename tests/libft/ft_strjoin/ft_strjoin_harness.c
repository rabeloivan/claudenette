#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_strjoin(char const *s1, char const *s2);

size_t	ft_strlen(const char *s);

/* free_tracker's redzone is the point here: a strjoin that allocates
 * len1 + len2 instead of len1 + len2 + 1 writes its terminator one byte past
 * the block, prints exactly the right answer, and would otherwise pass. */
int	main(int argc, char **argv)
{
	char	*out;

	if (argc != 3)
		return (1);
	out = ft_strjoin(argv[1], argv[2]);
	if (!out)
		return (write(1, "NULL", 4), 0);
	write(1, "[", 1);
	write(1, out, ft_strlen(out));
	write(1, "]", 1);
	h_check_redzones();
	return (0);
}
