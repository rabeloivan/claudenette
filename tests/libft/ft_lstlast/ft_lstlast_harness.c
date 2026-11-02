#include <stdlib.h>
#include <unistd.h>

#include "libft.h"

t_list	*ft_lstlast(t_list *lst);

static void	put_int(int n)
{
	char	c;

	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* Prints the index of the node returned, so "returned the last one" is
 * checked rather than merely "returned something non-NULL". */
int	main(int argc, char **argv)
{
	t_list	nodes[8];
	t_list	*ret;
	int		count;
	int		i;

	if (argc != 2)
		return (1);
	count = atoi(argv[1]);
	if (count == 0)
	{
		if (ft_lstlast(NULL) == NULL)
			return (write(1, "NULL", 4), 0);
		return (write(1, "NOTNULL", 7), 0);
	}
	i = 0;
	while (i < count)
	{
		nodes[i].content = (void *)"x";
		nodes[i].next = NULL;
		if (i > 0)
			nodes[i - 1].next = &nodes[i];
		i++;
	}
	ret = ft_lstlast(&nodes[0]);
	i = 0;
	while (i < count && ret != &nodes[i])
		i++;
	if (i == count)
		return (write(1, "UNKNOWN", 7), 0);
	put_int(i);
	return (0);
}
