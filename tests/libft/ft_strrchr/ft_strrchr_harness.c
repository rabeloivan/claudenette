#include <stdlib.h>
#include <unistd.h>

char	*ft_strrchr(const char *s, int c);

static void	put_int(int n)
{
	char	c;

	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* argv[1] is the haystack, argv[2] the int to search for. Prints the offset
 * of the returned pointer, or NULL. Searching for 0 must find the terminator
 * and return a pointer to it rather than NULL - that is the case students
 * most often miss, and it is index strlen(s) here. */
int	main(int argc, char **argv)
{
	char	*ret;

	if (argc != 3)
		return (1);
	ret = ft_strrchr(argv[1], atoi(argv[2]));
	if (ret == NULL)
		write(1, "NULL", 4);
	else
		put_int((int)(ret - argv[1]));
	return (0);
}
