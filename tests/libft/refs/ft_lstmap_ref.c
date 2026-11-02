#include <stdlib.h>

#include "libft_ref.h"

t_list	*ft_lstmap(t_list *lst, void *(*f)(void *), void (*del)(void *))
{
	t_list	*out;
	t_list	*node;
	void	*content;

	if (!lst || !f || !del)
		return (NULL);
	out = NULL;
	while (lst)
	{
		content = f(lst->content);
		node = ft_lstnew(content);
		if (!node)
		{
			del(content);
			ft_lstclear(&out, del);
			return (NULL);
		}
		ft_lstadd_back(&out, node);
		lst = lst->next;
	}
	return (out);
}
