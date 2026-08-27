#include <unistd.h>

#define DUMP_LEN 512

char	*ft_strncat(char *dest, char *src, unsigned int nb);

int	main(void)
{
	char			buffer[4096];
	char			dest[DUMP_LEN];
	char			*src;
	int				bytes_read;
	int				i;
	int				dest_len;
	int				j;
	unsigned int	nb;
	char			*ret;
	char			marker;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	i = 0;
	nb = 0;
	while (buffer[i] >= '0' && buffer[i] <= '9')
	{
		nb = nb * 10 + (buffer[i] - '0');
		i++;
	}
	if (buffer[i] == '\n')
		i++;
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
	ret = ft_strncat(dest, src, nb);
	if (ret == dest)
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, dest, DUMP_LEN);
	return (0);
}
