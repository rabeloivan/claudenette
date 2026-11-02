#include <unistd.h>

#include "libft_ref.h"

void	ft_putnbr_fd(int n, int fd)
{
	char			c;
	unsigned int	value;

	if (n < 0)
	{
		write(fd, "-", 1);
		value = (unsigned int)(-(long)n);
	}
	else
		value = (unsigned int)n;
	if (value >= 10)
		ft_putnbr_fd((int)(value / 10), fd);
	c = '0' + (value % 10);
	write(fd, &c, 1);
}
