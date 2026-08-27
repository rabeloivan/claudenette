#include <unistd.h>

char	*ft_strupcase(char *str);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	char	*ret;
	char	marker;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ret = ft_strupcase(buffer);
	if (ret == buffer)
		marker = '1';
	else
		marker = '0';
	write(1, &marker, 1);
	write(1, buffer, bytes_read);
	return (0);
}
