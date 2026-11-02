#include <stdlib.h>
#include <unistd.h>

void	ft_sort_string_tab(char **tab);

static void	put_str(char *s)
{
	while (*s)
		write(1, s++, 1);
}

int	main(void)
{
	char	buffer[4096];
	char	*tab[64];
	int		bytes_read;
	int		count;
	int		pos;
	int		idx;

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
	ft_sort_string_tab(tab);
	idx = 0;
	while (tab[idx] != 0)
	{
		if (idx > 0)
			write(1, "\x01", 1);
		put_str(tab[idx]);
		idx++;
	}
	return (0);
}
