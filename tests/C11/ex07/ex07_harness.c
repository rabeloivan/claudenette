#include <stdlib.h>
#include <unistd.h>

void	ft_advanced_sort_string_tab(char **tab, int (*cmp)(char *, char *));

static int	my_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] != '\0' && s1[i] == s2[i])
		i++;
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}

static int	cmp_asc(char *a, char *b)
{
	return (my_strcmp(a, b));
}

static int	cmp_desc(char *a, char *b)
{
	return (my_strcmp(b, a));
}

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
	int		cmp_type;
	int		count;
	int		pos;
	int		idx;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	cmp_type = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	count = atoi(buffer + pos);
	while (buffer[pos] != '\n' && buffer[pos] != '\0')
		pos++;
	if (buffer[pos] == '\n')
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
	if (cmp_type == 0)
		ft_advanced_sort_string_tab(tab, &cmp_asc);
	else
		ft_advanced_sort_string_tab(tab, &cmp_desc);
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
