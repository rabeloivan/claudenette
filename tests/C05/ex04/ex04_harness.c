#include <stdlib.h>
#include <unistd.h>

int	ft_fibonacci(int index);

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

int	main(void)
{
	char	buffer[64];
	int		bytes_read;
	int		index;
	int		ret;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	index = atoi(buffer);
	ret = ft_fibonacci(index);
	put_int(ret);
	return (0);
}
