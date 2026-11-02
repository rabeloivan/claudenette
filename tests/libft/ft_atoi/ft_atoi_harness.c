#include <unistd.h>

int	ft_atoi(const char *str);

static void	put_uint(unsigned int v)
{
	char	c;

	if (v >= 10)
		put_uint(v / 10);
	c = '0' + (v % 10);
	write(1, &c, 1);
}

/* Negation goes through long so INT_MIN prints correctly: -(int)INT_MIN
 * overflows, which is exactly the value ft_atoi is most often asked for. */
static void	put_int(int n)
{
	unsigned int	v;

	if (n < 0)
	{
		write(1, "-", 1);
		v = (unsigned int)(-(long)n);
	}
	else
		v = (unsigned int)n;
	put_uint(v);
}

int	main(int argc, char **argv)
{
	if (argc != 2)
		return (1);
	put_int(ft_atoi(argv[1]));
	return (0);
}
