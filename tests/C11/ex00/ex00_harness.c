#include <stdlib.h>
#include <unistd.h>

void	ft_foreach(int *tab, int length, void (*f)(int));

static int	g_count = 0;

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

static void	record(int n)
{
	if (g_count > 0)
		write(1, ",", 1);
	put_int(n);
	g_count++;
}

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		length;
	int		pos;
	int		idx;
	int		tab[256];

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
	ft_foreach(tab, length, &record);
	return (0);
}
