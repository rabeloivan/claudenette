#include <stdlib.h>
#include <unistd.h>

void	*ft_memcpy(void *dst, const void *src, size_t n);

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

/* dst is pre-filled with 0xAA so a copy that runs long shows up. src holds
 * 0x00..0x0f, which includes a NUL at index 0 - memcpy is byte-counted, not
 * NUL-terminated, and stopping early there is the classic confusion with
 * strcpy. */
int	main(int argc, char **argv)
{
	unsigned char	dst[16];
	unsigned char	src[16];
	void			*ret;
	int				sel;
	size_t			i;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	fill(dst, 16, 0xAA);
	i = 0;
	while (i < 16)
	{
		src[i] = (unsigned char)i;
		i++;
	}
	ret = dst;
	if (sel == 0)
		ret = ft_memcpy(dst, src, 16);
	else if (sel == 1)
		ret = ft_memcpy(dst + 4, src + 8, 4);
	else if (sel == 2)
		ret = ft_memcpy(dst, src, 0);
	put_hex(dst, 16);
	write(1, "|", 1);
	if ((sel == 1 && ret == dst + 4) || (sel != 1 && ret == dst))
		write(1, "R1", 2);
	else
		write(1, "R0", 2);
	return (0);
}
