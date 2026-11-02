#include "ft_stock_str.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct s_stock_str	*ft_strs_to_tab(int ac, char **av);

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
	char				buffer[4096];
	char				*av[64];
	int					bytes_read;
	int					ac;
	int					i;
	int					j;
	struct s_stock_str	*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ac = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n')
		i++;
	i++;
	j = 0;
	while (j < ac)
	{
		av[j] = buffer + i;
		while (buffer[i] != '\n' && buffer[i] != '\0')
			i++;
		buffer[i] = '\0';
		i++;
		j++;
	}
	ret = ft_strs_to_tab(ac, av);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	i = 0;
	while (i < ac)
	{
		if (i > 0)
			write(1, "\x02", 1);
		put_int(ret[i].size);
		write(1, "\x01", 1);
		write(1, ret[i].str, strlen(ret[i].str));
		write(1, "\x01", 1);
		write(1, ret[i].copy, strlen(ret[i].copy));
		write(1, "\x01", 1);
		if (ret[i].str == ret[i].copy)
			write(1, "1", 1);
		else
			write(1, "0", 1);
		i++;
	}
	if (ac > 0)
		write(1, "\x02", 1);
	if (ret[ac].str == NULL)
		write(1, "1", 1);
	else
		write(1, "0", 1);
	free(ret);
	return (0);
}
