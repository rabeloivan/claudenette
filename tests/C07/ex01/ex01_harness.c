#include <stdlib.h>
#include <unistd.h>

int	*ft_range(int min, int max);

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
	int		i;
	int		min;
	int		max;
	int		*ret;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	min = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n' && buffer[i] != '\0')
		i++;
	if (buffer[i] == '\n')
		i++;
	max = atoi(buffer + i);
	ret = ft_range(min, max);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	i = 0;
	while (i < max - min)
	{
		if (i > 0)
			write(1, ",", 1);
		put_int(ret[i]);
		i++;
	}
	free(ret);
	return (0);
}
