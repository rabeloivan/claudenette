#include <stdlib.h>
#include <unistd.h>

void	ft_putnbr_fd(int n, int fd);

int	main(int argc, char **argv)
{
	int	fd;

	if (argc != 3)
		return (1);
	fd = atoi(argv[2]);
	if (fd == 2)
	{
		write(1, "[", 1);
		ft_putnbr_fd(atoi(argv[1]), 2);
		write(1, "]", 1);
		return (0);
	}
	ft_putnbr_fd(atoi(argv[1]), 1);
	return (0);
}
