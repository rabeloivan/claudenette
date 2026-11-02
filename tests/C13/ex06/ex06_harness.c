#include "ft_btree.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

int	btree_level_count(t_btree *root);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	int		values[64];
	t_btree	*root;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	count = atoi(buffer);
	pos = 0;
	while (buffer[pos] != '\n')
		pos++;
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
	h_put_int(btree_level_count(root));
	return (0);
}
