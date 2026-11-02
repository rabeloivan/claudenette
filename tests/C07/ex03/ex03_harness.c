#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char	*ft_strjoin(int size, char **strs, char *sep);

int	main(void)
{
	char	buffer[4096];
	char	*strs[64];
	char	*sep;
	int		bytes_read;
	int		i;
	int		j;
	int		size;
	char	*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	size = atoi(buffer);
	i = 0;
	while (buffer[i] != '\n')
		i++;
	i++;
	sep = buffer + i;
	while (buffer[i] != '\n')
		i++;
	buffer[i] = '\0';
	i++;
	j = 0;
	while (j < size)
	{
		strs[j] = buffer + i;
		while (buffer[i] != '\n' && buffer[i] != '\0')
			i++;
		buffer[i] = '\0';
		i++;
		j++;
	}
	ret = ft_strjoin(size, strs, sep);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	write(1, ret, strlen(ret));
	free(ret);
	return (0);
}
