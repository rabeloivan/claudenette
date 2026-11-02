#include <unistd.h>

int	ft_str_is_uppercase(char *str);

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
	char	buffer[4096];
	int		bytes_read;
	int		ret;

	bytes_read = read_all(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ret = ft_str_is_uppercase(buffer);
	put_int(ret);
	return (0);
}
