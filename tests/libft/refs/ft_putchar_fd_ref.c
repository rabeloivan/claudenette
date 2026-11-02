#include <unistd.h>

#include "libft_ref.h"

void	ft_putchar_fd(char c, int fd)
{
	write(fd, &c, 1);
}
