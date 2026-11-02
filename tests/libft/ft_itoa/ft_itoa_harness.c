#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

char	*ft_itoa(int n);

size_t	ft_strlen(const char *s);

/* argv[1] is parsed with strtol rather than atoi so INT_MIN survives the
 * round trip on every platform. */
int	main(int argc, char **argv)
{
	char	*out;

	if (argc != 2)
		return (1);
	out = ft_itoa((int)strtol(argv[1], NULL, 10));
	if (!out)
		return (write(1, "NULL", 4), 0);
	write(1, out, ft_strlen(out));
	h_check_redzones();
	return (0);
}
