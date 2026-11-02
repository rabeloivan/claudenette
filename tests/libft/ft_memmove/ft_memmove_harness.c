#include <stdlib.h>
#include <unistd.h>

void	*ft_memmove(void *dst, const void *src, size_t len);

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

/* The whole point of memmove over memcpy is overlapping regions, so both
 * overlap directions are covered: dst>src (a naive forward loop corrupts the
 * tail) and dst<src (a naive backward loop corrupts it instead). A student
 * who only special-cased one direction passes memcpy's tests and fails here. */
int	main(int argc, char **argv)
{
	unsigned char	buf[16];
	void			*ret;
	int				sel;
	size_t			i;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	i = 0;
	while (i < 16)
	{
		buf[i] = (unsigned char)i;
		i++;
	}
	ret = buf;
	if (sel == 0)
		ret = ft_memmove(buf + 4, buf, 8);
	else if (sel == 1)
		ret = ft_memmove(buf, buf + 4, 8);
	else if (sel == 2)
		ret = ft_memmove(buf + 2, buf + 2, 6);
	else if (sel == 3)
		ret = ft_memmove(buf, buf + 1, 0);
	put_hex(buf, 16);
	write(1, "|", 1);
	if ((sel == 0 && ret == buf + 4) || (sel == 2 && ret == buf + 2)
		|| ((sel == 1 || sel == 3) && ret == buf))
		write(1, "R1", 2);
	else
		write(1, "R0", 2);
	return (0);
}
