#include <unistd.h>

void	ft_putchar(char c);

int	main(void)
{
	char	c;

	while (read(0, &c, 1) > 0)
	{
		ft_putchar(c);
	}
	return (0);
}
