#include <unistd.h>

int	ft_ten_queens_puzzle(void);

static void	put_int(int n)
{
	char	c;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

int	main(void)
{
	int	ret;

	ret = ft_ten_queens_puzzle();
	write(1, "|", 1);
	put_int(ret);
	return (0);
}
