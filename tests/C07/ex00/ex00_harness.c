#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char	*ft_strdup(char *src);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	char	*ret;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ret = ft_strdup(buffer);
	if (ret == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	if (ret == buffer)
		write(1, "S", 1);
	else
		write(1, "D", 1);
	write(1, ret, strlen(ret));
	free(ret);
	return (0);
}
