#include <stdlib.h>
#include <unistd.h>

void	*ft_memset(void *b, int c, size_t len);

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

/* Prints the whole 16-byte buffer as hex, then |R1 or |R0 for whether the
 * return value was the pointer that was passed in - the subject's man-page
 * behaviour, and a return a student often forgets. The buffer is pre-filled
 * with 0xAA so an under- or over-write past the requested length shows up as
 * a changed byte rather than blending into zeroed memory. */
int	main(int argc, char **argv)
{
	unsigned char	buf[16];
	void			*ret;
	int				sel;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	fill(buf, 16, 0xAA);
	ret = buf;
	if (sel == 0)
		ret = ft_memset(buf + 2, 0x5A, 10);
	else if (sel == 1)
		ret = ft_memset(buf + 4, 0x5A, 0);
	else if (sel == 2)
		ret = ft_memset(buf, 0x141, 16);
	else if (sel == 3)
		ret = ft_memset(buf, 0, 16);
	put_hex(buf, 16);
	write(1, "|", 1);
	if ((sel == 0 && ret == buf + 2) || (sel == 1 && ret == buf + 4)
		|| (sel >= 2 && ret == buf))
		write(1, "R1", 2);
	else
		write(1, "R0", 2);
	return (0);
}
