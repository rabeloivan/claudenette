#include <stdlib.h>
#include <unistd.h>

void	ft_bzero(void *s, size_t n);

static void	put_hex(const unsigned char *p, size_t n)
{
	const char	*digits = "0123456789abcdef";
	size_t		i;
	char		out[2];

	i = 0;
	while (i < n)
	{
		out[0] = digits[p[i] >> 4];
		out[1] = digits[p[i] & 15];
		write(1, out, 2);
		i++;
	}
}

static void	fill(unsigned char *p, size_t n, unsigned char v)
{
	size_t	i;

	i = 0;
	while (i < n)
		p[i++] = v;
}

/* 0xAA pre-fill again, so "zeroed the right range and nothing else" is
 * visible in the dump: a length that runs one byte long or short changes a
 * byte that should still read aa. */
int	main(int argc, char **argv)
{
	unsigned char	buf[16];
	int				sel;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	fill(buf, 16, 0xAA);
	if (sel == 0)
		ft_bzero(buf + 3, 8);
	else if (sel == 1)
		ft_bzero(buf + 4, 0);
	else if (sel == 2)
		ft_bzero(buf, 16);
	put_hex(buf, 16);
	return (0);
}
