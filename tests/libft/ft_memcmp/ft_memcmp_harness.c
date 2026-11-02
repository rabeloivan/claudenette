#include <stdlib.h>
#include <unistd.h>

int	ft_memcmp(const void *s1, const void *s2, size_t n);

/* Prints only the SIGN of the return value. The C standard fixes the sign but
 * not the magnitude, and real libcs differ, so comparing the exact number
 * would fail a correct submission. The sign is still enough to catch the bug
 * this function is prone to: comparing as signed char, which inverts the
 * result as soon as a byte goes above 0x7f - case 3 below is exactly that. */
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
	unsigned char	a[8];
	unsigned char	b[8];
	int				sel;
	size_t			i;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	i = 0;
	while (i < 8)
	{
		a[i] = (unsigned char)(i + 1);
		b[i] = (unsigned char)(i + 1);
		i++;
	}
	if (sel == 1)
		b[3] = 0x00;
	else if (sel == 2)
		a[3] = 0x00;
	else if (sel == 3)
	{
		a[2] = 0x80;
		b[2] = 0x01;
	}
	else if (sel == 4)
		b[7] = 0xFF;
	if (sel == 5)
		put_sign(ft_memcmp(a, b, 0));
	else if (sel == 6)
	{
		b[0] = 0xFF;
		put_sign(ft_memcmp(a, b, 0));
	}
	else
		put_sign(ft_memcmp(a, b, 8));
	return (0);
}
