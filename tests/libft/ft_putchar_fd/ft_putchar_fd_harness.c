#include <stdlib.h>
#include <unistd.h>

void	ft_putchar_fd(char c, int fd);

/* argv[2] picks the descriptor. The fd=2 case brackets the call with markers
 * written to stdout: if the function ignores its fd argument and writes to 1
 * anyway, the payload lands between the brackets and the comparison fails.
 * Without that, a hardcoded write(1, ...) would pass every stdout test. */
int	main(int argc, char **argv)
{
	int	fd;

	if (argc != 3)
		return (1);
	fd = atoi(argv[2]);
	if (fd == 2)
	{
		write(1, "[", 1);
		ft_putchar_fd(argv[1][0], 2);
		write(1, "]", 1);
		return (0);
	}
	ft_putchar_fd(argv[1][0], 1);
	return (0);
}
