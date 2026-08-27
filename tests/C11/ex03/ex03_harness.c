#include <stdlib.h>
#include <unistd.h>

int	ft_count_if(char **tab, int length, int (*f)(char *));

static int	has_digit(char *s)
{
	int	i;

	i = 0;
	while (s[i] != '\0')
	{
		if (s[i] >= '0' && s[i] <= '9')
			return (1);
		i++;
	}
	return (0);
}

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
	char	buffer[4096];
	char	*tab[64];
	int		bytes_read;
	int		count;
	int		pos;
	int		idx;
	int		ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	count = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	idx = 0;
	while (idx < count)
	{
		tab[idx] = buffer + pos;
		while (buffer[pos] != '\n' && buffer[pos] != '\0')
			pos++;
		buffer[pos] = '\0';
		pos++;
		idx++;
	}
	tab[idx] = 0;
	ret = ft_count_if(tab, count, &has_digit);
	put_int(ret);
	return (0);
}
