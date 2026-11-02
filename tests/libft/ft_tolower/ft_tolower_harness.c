#include <stdlib.h>
#include <unistd.h>

int	ft_tolower(int c);

static void	put_int(int n)
{
	char	c;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* argv[1]..argv[2] inclusive, comma-separated. Sweeping the range rather than
 * sampling catches the common failure where only one of the two case ranges
 * is handled, and the off-by-one at 'z'/'Z' and '{'/'['. */
int	main(int argc, char **argv)
{
	int	c;

	if (argc != 3)
		return (1);
	c = atoi(argv[1]);
	while (c <= atoi(argv[2]))
	{
		if (c != atoi(argv[1]))
			write(1, ",", 1);
		put_int(ft_tolower(c));
		c++;
	}
	return (0);
}
