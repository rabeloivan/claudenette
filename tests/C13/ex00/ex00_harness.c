#include "ft_btree.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_btree	*btree_create_node(void *item);

int	main(void)
{
	char	buffer[64];
	int		bytes_read;
	int		item;
	t_btree	*node;

	bytes_read = read(0, buffer, 63);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	item = atoi(buffer);
	node = btree_create_node((void *)(long)item);
	if (node == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	h_put_int((int)(long)node->item);
	write(1, ",", 1);
	h_put_int(node->left == NULL ? 1 : 0);
	write(1, ",", 1);
	h_put_int(node->right == NULL ? 1 : 0);
	return (0);
}
