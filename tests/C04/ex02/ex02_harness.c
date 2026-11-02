#include <stdlib.h>
#include <unistd.h>

void	ft_putnbr(int nb);

int	main(void)
{
	char	buffer[64];
	int		bytes_read;
	int		nb;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	nb = atoi(buffer);
	ft_putnbr(nb);
	return (0);
}
