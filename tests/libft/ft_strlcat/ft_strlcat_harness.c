#include <stdlib.h>
#include <unistd.h>

size_t	ft_strlcat(char *dst, const char *src, size_t dstsize);

static void	put_size(size_t n)
{
	char	c;

	if (n >= 10)
		put_size(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

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

/* argv[1] is dst's initial content, argv[2] is src, argv[3] is dstsize.
 * Output is "<return>|<16-byte dst dump>". The dump matters as much as the
 * return value: it shows exactly where the NUL landed and proves nothing was
 * written past dstsize. dst is pre-filled with 0x2a ('*') past its initial
 * content so an overrun is visible instead of blending into zeros. */
int	main(int argc, char **argv)
{
	unsigned char	dst[16];
	size_t			i;
	size_t			ret;

	if (argc != 4)
		return (1);
	i = 0;
	while (i < 16)
		dst[i++] = 0x2A;
	i = 0;
	while (argv[1][i])
	{
		dst[i] = (unsigned char)argv[1][i];
		i++;
	}
	dst[i] = '\0';
	ret = ft_strlcat((char *)dst, argv[2], (size_t)atoi(argv[3]));
	put_size(ret);
	write(1, "|", 1);
	put_hex(dst, 16);
	return (0);
}
