#include <stdlib.h>
#include <unistd.h>

#include "libft.h"

void	ft_lstiter(t_list *lst, void (*f)(void *));

size_t	ft_strlen(const char *s);

/* f mutates the content in place, so the check is on the list afterwards
 * rather than on anything f returns - the subject gives ft_lstiter no return
 * value and no allocation. */
static void	upper(void *content)
{
	char	*s;

	s = (char *)content;
	while (*s)
	{
		if (*s >= 'a' && *s <= 'z')
			*s -= 32;
		s++;
	}
}

int	main(int argc, char **argv)
{
	t_list	nodes[3];
	char	a[4];
	char	b[4];
	char	c[4];
	int		i;

	if (argc != 2)
		return (1);
	a[0] = 'a';
	a[1] = 'b';
	a[2] = '\0';
	b[0] = 'c';
	b[1] = 'd';
	b[2] = '\0';
	c[0] = 'e';
	c[1] = 'f';
	c[2] = '\0';
	nodes[0].content = a;
	nodes[1].content = b;
	nodes[2].content = c;
	nodes[0].next = &nodes[1];
	nodes[1].next = &nodes[2];
	nodes[2].next = NULL;
	if (atoi(argv[1]) == 0)
		ft_lstiter(NULL, upper);
	else
		ft_lstiter(&nodes[0], upper);
	i = 0;
	while (i < 3)
	{
		write(1, "[", 1);
		write(1, nodes[i].content, ft_strlen(nodes[i].content));
		write(1, "]", 1);
		i++;
	}
	return (0);
}
