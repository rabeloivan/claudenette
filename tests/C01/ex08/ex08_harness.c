#include <stdio.h>
#include <string.h>

void	ft_sort_int_tab(int *tab, int size);

int	main(int argc, char **argv)
{
	int	size;
	int	tab[1000];
	int	i;

	if (argc > 1 && strcmp(argv[1], "null_tab") == 0)
	{
		ft_sort_int_tab(NULL, 3);
		printf("OK");
		return (0);
	}
	if (scanf("%d", &size) == 1 && size >= 0 && size <= 1000)
	{
		i = 0;
		while (i < size)
		{
			scanf("%d", &tab[i]);
			i++;
		}
		ft_sort_int_tab(tab, size);
		i = 0;
		while (i < size)
		{
			printf("%d", tab[i]);
			if (i < size - 1)
				printf(" ");
			i++;
		}
	}
	return (0);
}
