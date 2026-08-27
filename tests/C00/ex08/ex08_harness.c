#include <unistd.h>
#include <stdlib.h>

void	ft_print_combn(int n);

int	main(void)
{
	char	buffer[10];
	int		bytes_read;

	bytes_read = read(0, buffer, 9);
	if (bytes_read > 0)
	{
		buffer[bytes_read] = '\0';
		ft_print_combn(atoi(buffer));
	}
	return (0);
}
