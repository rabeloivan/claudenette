#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"
#include "libft.h"

void	ft_lstclear(t_list **lst, void (*del)(void *));

static int	g_del_calls;

static void	del(void *content)
{
	g_del_calls++;
	free(content);
}

static void	put_int(int n)
{
	char	c;

	if (n >= 10)
		put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

/* Prints "<del calls>|<leaked>|<head is NULL>".
 *
 * Two separate obligations, and an implementation can satisfy one without the
 * other: calling del on every content while never freeing a node leaks three
 * nodes, and freeing everything while forgetting "set the pointer to the list
 * to NULL" leaves the caller with a dangling head. h_leaked_count covers the
 * first, the head check the second. */
int	main(void)
{
	t_list	*head;
	t_list	*node;
	int		i;

	head = NULL;
	i = 0;
	while (i < 3)
	{
		node = malloc(sizeof(t_list));
		if (!node)
			return (write(1, "ALLOCFAIL", 9), 0);
		node->content = malloc(2);
		if (!node->content)
			return (write(1, "ALLOCFAIL", 9), 0);
		((char *)node->content)[0] = 'a' + i;
		((char *)node->content)[1] = '\0';
		node->next = head;
		h_track(node);
		h_track(node->content);
		head = node;
		i++;
	}
	ft_lstclear(&head, del);
	put_int(g_del_calls);
	write(1, "|", 1);
	put_int(h_leaked_count());
	write(1, "|", 1);
	if (head == NULL)
		write(1, "HEADNULL", 8);
	else
		write(1, "HEADSET", 7);
	return (0);
}
