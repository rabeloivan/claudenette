#include <stdlib.h>
#include <unistd.h>

#include "libft.h"

unsigned int	ft_lstsize(t_list *lst);

static void	put_uint(unsigned int v)
{
	char	c;

	if (v >= 10)
		put_uint(v / 10);
	c = '0' + (v % 10);
	write(1, &c, 1);
}

/* argv[1] is how many nodes to chain up, so a single harness covers the empty
 * list, one node and many. The nodes are built here rather than through
 * ft_lstnew so a broken ft_lstnew cannot make ft_lstsize look wrong. */
int	main(int argc, char **argv)
{
	t_list	nodes[8];
	int		count;
	int		i;

	if (argc != 2)
		return (1);
	count = atoi(argv[1]);
	if (count == 0)
		return (put_uint(ft_lstsize(NULL)), 0);
	i = 0;
	while (i < count)
	{
		nodes[i].content = (void *)"x";
		nodes[i].next = NULL;
		if (i > 0)
			nodes[i - 1].next = &nodes[i];
		i++;
	}
	put_uint(ft_lstsize(&nodes[0]));
	return (0);
}
