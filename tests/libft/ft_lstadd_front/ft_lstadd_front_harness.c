#include <stdlib.h>
#include <unistd.h>

#include "libft.h"

void	ft_lstadd_front(t_list **lst, t_list *new);

size_t	ft_strlen(const char *s);

static void	print_list(t_list *lst)
{
	while (lst)
	{
		write(1, "[", 1);
		write(1, lst->content, ft_strlen(lst->content));
		write(1, "]", 1);
		lst = lst->next;
	}
}

/* Nodes are built by hand, not via ft_lstnew, so this grades ft_lstadd_front alone.
 * Case 0 starts from an empty list, which is where the two-pointer handling
 * usually breaks: *lst is NULL and must become the new node. */
int	main(int argc, char **argv)
{
	t_list	a;
	t_list	b;
	t_list	fresh;
	t_list	*head;
	int		sel;

	if (argc != 2)
		return (1);
	sel = atoi(argv[1]);
	a.content = (void *)"a";
	a.next = &b;
	b.content = (void *)"b";
	b.next = NULL;
	fresh.content = (void *)"new";
	fresh.next = NULL;
	if (sel == 0)
	{
		head = NULL;
		ft_lstadd_front(&head, &fresh);
	}
	else
	{
		head = &a;
		ft_lstadd_front(&head, &fresh);
	}
	print_list(head);
	return (0);
}
