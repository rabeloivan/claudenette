#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_strtrim(char const *s1, char const *set);

size_t	ft_strlen(const char *s);

int	main(int argc, char **argv)
{
	char	*out;

	if (argc != 3)
		return (1);
	out = ft_strtrim(argv[1], argv[2]);
	if (!out)
		return (write(1, "NULL", 4), 0);
	write(1, "[", 1);
	write(1, out, ft_strlen(out));
	write(1, "]", 1);
	h_check_redzones();
	return (0);
}
