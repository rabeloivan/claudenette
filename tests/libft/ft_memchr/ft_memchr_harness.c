#include <stdlib.h>
#include <unistd.h>

void	*ft_memchr(const void *s, int c, size_t n);

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

/* Prints the offset of the returned pointer, or NULL. The buffer contains a
 * 0x00 byte in the middle so "searching for 0" - which must find that byte
 * rather than stopping at it - is covered, and a 0x41 byte beyond the search
 * length so an implementation that ignores n is caught. */
int	main(int argc, char **argv)
{
	unsigned char	buf[8];
	void			*ret;
	int				sel;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	buf[0] = 0x10;
	buf[1] = 0x41;
	buf[2] = 0x00;
	buf[3] = 0x42;
	buf[4] = 0x41;
	buf[5] = 0xAA;
	buf[6] = 0x41;
	buf[7] = 0xFF;
	ret = NULL;
	if (sel == 0)
		ret = ft_memchr(buf, 0x42, 8);
	else if (sel == 1)
		ret = ft_memchr(buf, 0x00, 8);
	else if (sel == 2)
		ret = ft_memchr(buf, 0x41, 8);
	else if (sel == 3)
		ret = ft_memchr(buf, 0x41, 1);
	else if (sel == 4)
		ret = ft_memchr(buf, 0x99, 8);
	else if (sel == 5)
		ret = ft_memchr(buf, 0xAA, 8);
	else if (sel == 6)
		ret = ft_memchr(buf, 0x341, 8);
	else if (sel == 7)
		ret = ft_memchr(buf, 0x10, 0);
	if (ret == NULL)
		write(1, "NULL", 4);
	else
		put_int((int)((unsigned char *)ret - buf));
	return (0);
}
