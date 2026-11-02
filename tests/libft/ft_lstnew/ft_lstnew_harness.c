#include <stdlib.h>
#include <unistd.h>

#include "../../free_tracker.h"

/* t_list comes from the student's own libft.h - the subject says to "add the
 * following structure declaration to your libft.h file", so a
 * submission whose header lacks it fails to compile here, which is the
 * correct verdict. The standalone header test checks all 43 prototypes. */
#include "libft.h"

t_list	*ft_lstnew(void *content);

size_t	ft_strlen(const char *s);

int	main(int argc, char **argv)
{
	t_list	*node;

	if (argc != 2)
		return (1);
	node = ft_lstnew(argv[1]);
	if (!node)
		return (write(1, "NULL", 4), 0);
	write(1, "[", 1);
	if (node->content)
		write(1, node->content, ft_strlen(node->content));
	write(1, "]", 1);
	if (node->content == argv[1])
		write(1, "|SAMEPTR", 8);
	else
		write(1, "|COPIED", 7);
	if (node->next == NULL)
		write(1, "|NEXTNULL", 9);
	else
		write(1, "|NEXTSET", 8);
	h_check_redzones();
	return (0);
}
