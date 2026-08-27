#include "ft_btree.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

void	*btree_search_item(t_btree *root, void *data_ref,
			int (*cmpf)(void *, void *));

int	main(int argc, char **argv)
{
	char	buffer[4096];
	int		bytes_read;
	int		pos;
	int		i;
	int		count;
	int		ref;
	int		values[64];
	t_btree	*root;
	void	*found;

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 4;
		values[1] = 2;
		values[2] = 6;
		root = h_build_tree(values, 3);
		found = btree_search_item(root, (void *)(long)2, NULL);
		(void)found;
		write(1, "OK\n", 3);
		return (0);
	}
	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	ref = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
	pos++;
	count = atoi(buffer + pos);
	while (buffer[pos] != '\n' && buffer[pos] != '\0')
		pos++;
	if (buffer[pos] == '\n')
		pos++;
	i = 0;
	while (i < count)
	{
		values[i] = atoi(buffer + pos);
		while (buffer[pos] != ',' && buffer[pos] != '\0')
			pos++;
		if (buffer[pos] == ',')
			pos++;
		i++;
	}
	root = h_build_tree(values, count);
	found = btree_search_item(root, (void *)(long)ref, &h_cmp_int_asc);
	if (found == NULL)
	{
		write(1, "N", 1);
		return (0);
	}
	write(1, "A", 1);
	h_put_int((int)(long)found);
	return (0);
}
