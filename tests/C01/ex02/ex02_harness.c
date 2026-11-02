#include <stdio.h>
#include <string.h>

void	ft_swap(int *a, int *b);

int	main(int argc, char **argv)
{
	int	a;
	int	b;

	if (argc > 1 && strcmp(argv[1], "null_a") == 0)
	{
		b = 1;
		ft_swap(NULL, &b);
		printf("OK");
		return (0);
	}
	if (argc > 1 && strcmp(argv[1], "null_b") == 0)
	{
		a = 1;
		ft_swap(&a, NULL);
		printf("OK");
		return (0);
	}
	if (scanf("%d %d", &a, &b) == 2)
	{
		ft_swap(&a, &b);
		printf("%d %d", a, b);
	}
	return (0);
}
