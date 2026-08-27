#include <unistd.h>

void	ft_putstr_non_printable(char *str);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ft_putstr_non_printable(buffer);
	return (0);
}
