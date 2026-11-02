#include <unistd.h>

char	*ft_strstr(char *str, char *to_find);

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
	char	to_find[4096];
	char	*str;
	int		bytes_read;
	int		i;
	int		to_find_len;
	int		j;
	char	*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	to_find_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		to_find_len = to_find_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < to_find_len)
	{
		to_find[j] = buffer[i + j];
		j++;
	}
	to_find[j] = '\0';
	str = buffer + i + to_find_len;
	ret = ft_strstr(str, to_find);
	if (ret == 0)
		put_int(-1);
	else
		put_int((int)(ret - str));
	return (0);
}
