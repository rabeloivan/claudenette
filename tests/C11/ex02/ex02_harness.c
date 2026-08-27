#include <stdlib.h>
#include <unistd.h>

int	ft_any(char **tab, int (*f)(char *));

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
	ret = ft_any(tab, &has_digit);
	if (ret)
		write(1, "1", 1);
	else
		write(1, "0", 1);
	return (0);
}
