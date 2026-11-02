#include <unistd.h>

int	ft_strncmp(char *s1, char *s2, unsigned int n);

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

/*
** All of stdin rather than one read(): Python's subprocess writes a test's
** input in PIPE_BUF chunks - 512 bytes on macOS - so for the cases here, up
** to 2000 bytes, a single read() can return only the first chunk when the
** machine is loaded, and the student's function is handed a truncated
** string.
*/
static int	read_all(int fd, char *buf, int cap)
{
	int	total;
	int	r;

	total = 0;
	r = read(fd, buf, cap);
	while (r > 0)
	{
		total += r;
		r = read(fd, buf + total, cap - total);
	}
	if (r < 0 && total == 0)
		return (-1);
	return (total);
}

int	main(void)
{
	char			buffer[4096];
	char			s1[4096];
	char			*s2;
	int				bytes_read;
	int				i;
	unsigned int	n;
	int				s1_len;
	int				j;
	int				ret;

	bytes_read = read_all(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	n = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		n = n * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	s1_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		s1_len = s1_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < s1_len)
	{
		s1[j] = buffer[i + j];
		j++;
	}
	s1[j] = '\0';
	s2 = buffer + i + s1_len;
	ret = ft_strncmp(s1, s2, n);
	put_int(ret);
	return (0);
}
