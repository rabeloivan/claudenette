#include <stdlib.h>
#include <unistd.h>

int	ft_is_sort(int *tab, int length, int (*f)(int, int));

static int	cmp_asc(int a, int b)
{
	return (a - b);
}

static int	cmp_desc(int a, int b)
{
	return (b - a);
}

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		cmp_type;
	int		length;
	int		pos;
	int		idx;
	int		tab[256];
	int		ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	cmp_type = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	length = atoi(buffer + pos);
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
	if (cmp_type == 0)
		ret = ft_is_sort(tab, length, &cmp_asc);
	else
		ret = ft_is_sort(tab, length, &cmp_desc);
	if (ret)
		write(1, "1", 1);
	else
		write(1, "0", 1);
	return (0);
}
