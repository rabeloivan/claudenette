#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"
#include "libft.h"

void	ft_lstdelone(t_list *lst, void (*del)(void *));

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

/* Prints "<del calls>|<node frees>|<content frees>|<next frees>".
 *
 * The last field is the point: the subject says "Free the node itself but
 * does NOT free the next node." An implementation that walks the rest of the
 * list produces identical visible behaviour in every other respect, so only
 * counting frees per pointer can tell them apart - which is what
 * h_free_count_of exists for. */
int	main(void)
{
	t_list	*node;
	t_list	*next;
	char	*content;

	node = malloc(sizeof(t_list));
	next = malloc(sizeof(t_list));
	content = malloc(4);
	if (!node || !next || !content)
		return (write(1, "ALLOCFAIL", 9), 0);
	content[0] = 'a';
	content[1] = 'b';
	content[2] = 'c';
	content[3] = '\0';
	node->content = content;
	node->next = next;
	next->content = NULL;
	next->next = NULL;
	h_track(node);
	h_track(next);
	h_track(content);
	ft_lstdelone(node, del);
	put_int(g_del_calls);
	write(1, "|", 1);
	put_int(h_free_count_of(node));
	write(1, "|", 1);
	put_int(h_free_count_of(content));
	write(1, "|", 1);
	put_int(h_free_count_of(next));
	return (0);
}
