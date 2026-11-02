#include <unistd.h>
#include <stdlib.h>

void	ft_is_negative(int n);

int	main(void)
{
	char	buffer[50];
	int		bytes_read;

	bytes_read = read(0, buffer, 49);
	if (bytes_read > 0)
	{
		buffer[bytes_read] = '\0';
		ft_is_negative(atoi(buffer));
	}
	return (0);
}
