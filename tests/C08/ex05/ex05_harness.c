#include "ft_stock_str.h"
#include <unistd.h>

void	ft_show_tab(struct s_stock_str *par);

int	main(void)
{
	struct s_stock_str	tab[4];

	tab[0].size = 5;
	tab[0].str = "hello";
	tab[0].copy = "hello";
	tab[1].size = 3;
	tab[1].str = "abc";
	tab[1].copy = "XYZ";
	tab[2].size = 99;
	tab[2].str = "hi";
	tab[2].copy = "hi";
	tab[3].size = 0;
	tab[3].str = 0;
	tab[3].copy = 0;
	ft_show_tab(tab);
	return (0);
}
