#include <stdlib.h>
#include <unistd.h>

int	ft_strncmp(const char *s1, const char *s2, size_t n);

/* Sign only: the standard fixes the sign of the result but not its magnitude,
 * and libcs differ. The sign still catches the characteristic bug - comparing
 * as signed char, which inverts the answer once a byte exceeds 0x7f. */
static void	put_sign(int v)
{
	if (v > 0)
		write(1, "+", 1);
	else if (v < 0)
		write(1, "-", 1);
	else
		write(1, "0", 1);
}

int	main(int argc, char **argv)
{
	if (argc != 4)
		return (1);
	put_sign(ft_strncmp(argv[1], argv[2], (size_t)atoi(argv[3])));
	return (0);
}
