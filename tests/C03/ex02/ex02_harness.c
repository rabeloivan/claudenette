#include <unistd.h>

#define DUMP_LEN 512

char	*ft_strcat(char *dest, char *src);

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
	char	dest[DUMP_LEN];
	char	*src;
	int		bytes_read;
	int		i;
	int		dest_len;
	int		j;
	char	*ret;
	char	marker;

	bytes_read = read_all(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	dest_len = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		dest_len = dest_len * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
	j = 0;
	while (j < DUMP_LEN)
	{
		dest[j] = (char)0xFF;
		j++;
	}
	j = 0;
	while (j < dest_len)
	{
		dest[j] = buffer[i + j];
		j++;
	}
	dest[j] = '\0';
	src = buffer + i + dest_len;
	ret = ft_strcat(dest, src);
	if (ret == dest)
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, dest, DUMP_LEN);
	return (0);
}
