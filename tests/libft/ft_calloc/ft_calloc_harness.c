#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

void	*ft_calloc(size_t count, size_t size);

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

/* Linked against free_tracker.c, so malloc hands back 0xAA-poisoned memory
 * rather than the freshly-zeroed pages the real allocator usually supplies.
 * Without that a ft_calloc which allocates but never zeroes passes every run
 * by luck; here it prints aaaa... and fails. */
int	main(int argc, char **argv)
{
	unsigned char	*p;
	int				sel;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	if (sel == 0)
	{
		p = ft_calloc(16, 1);
		if (!p)
			return (write(1, "NULL", 4), 0);
		put_hex(p, 16);
	}
	else if (sel == 1)
	{
		p = ft_calloc(4, 4);
		if (!p)
			return (write(1, "NULL", 4), 0);
		put_hex(p, 16);
	}
	else if (sel == 2)
	{
		p = ft_calloc(0, 0);
		if (p)
			write(1, "NONNULL", 7);
		else
			write(1, "NULL", 4);
	}
	else if (sel == 3)
	{
		p = ft_calloc(0, 5);
		if (p)
			write(1, "NONNULL", 7);
		else
			write(1, "NULL", 4);
	}
	else if (sel == 4 || sel == 5)
	{
		/* count * size wraps: to 2 bytes for case 4, to 1 for case 5. */
		if (sel == 4)
			p = ft_calloc(SIZE_MAX / 2 + 2, 2);
		else
			p = ft_calloc(SIZE_MAX, SIZE_MAX);
		if (p)
			write(1, "NONNULL", 7);
		else
			write(1, "NULL", 4);
	}
	h_check_redzones();
	return (0);
}
