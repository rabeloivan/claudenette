#include <stdlib.h>
#include <unistd.h>

int	*ft_map(int *tab, int length, int (*f)(int));

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

static int	square(int n)
{
	return (n * n);
}

static void	put_tab(int *tab, int length)
{
	int	i;

	i = 0;
	while (i < length)
	{
		if (i > 0)
			write(1, ",", 1);
		put_int(tab[i]);
		i++;
	}
}

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		length;
	int		pos;
	int		idx;
	int		tab[256];
	int		*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	length = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n' && buffer[pos] != '\0')
		pos++;
	if (buffer[pos] == '\n')
		pos++;
	idx = 0;
	while (idx < length)
	{
		tab[idx] = atoi(buffer + pos);
		while (buffer[pos] != ',' && buffer[pos] != '\0')
			pos++;
		if (buffer[pos] == ',')
			pos++;
		idx++;
	}
	ret = ft_map(tab, length, &square);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	put_tab(ret, length);
	write(1, "|", 1);
	put_tab(tab, length);
	free(ret);
	return (0);
}
