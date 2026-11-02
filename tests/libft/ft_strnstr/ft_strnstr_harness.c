#include <stdlib.h>
#include <unistd.h>

char	*ft_strnstr(const char *haystack, const char *needle, size_t len);

static void	put_int(int n)
{
	char	c;

	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* argv[1] haystack, argv[2] needle, argv[3] len. Prints the match offset or
 * NULL. len bounds the HAYSTACK, not the needle: a match that would start
 * inside len but run past it does not count, which is case 5 in the test. */
int	main(int argc, char **argv)
{
	char	*ret;

	if (argc != 4)
		return (1);
	ret = ft_strnstr(argv[1], argv[2], (size_t)atoi(argv[3]));
	if (ret == NULL)
		write(1, "NULL", 4);
	else
		put_int((int)(ret - argv[1]));
	return (0);
}
