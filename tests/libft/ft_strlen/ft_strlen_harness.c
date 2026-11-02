#include <stdlib.h>
#include <unistd.h>

size_t	ft_strlen(const char *s);

static void	put_size(size_t n)
{
	char	c;

	if (n >= 10)
		put_size(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

int	main(int argc, char **argv)
{
	if (argc != 2)
		return (1);
	put_size(ft_strlen(argv[1]));
	return (0);
}
