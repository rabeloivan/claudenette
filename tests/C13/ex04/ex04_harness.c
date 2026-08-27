#include "ft_btree.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

void	btree_insert_data(t_btree **root, void *item, int (*cmpf)(void *, void *));

static void	print_prefix(t_btree *root, int *first)
{
	if (root == NULL)
		return ;
	if (*first == 0)
		write(1, ",", 1);
	*first = 0;
	h_put_int((int)(long)root->item);
	print_prefix(root->left, first);
	print_prefix(root->right, first);
}

int	main(int argc, char **argv)
{
	char	buffer[4096];
	int		bytes_read;
	int		pos;
	int		i;
	int		count;
	int		values[64];
	t_btree	*root;
	int		(*cmpf)(void *, void *);
	int		first;

	if (h_null_callback_mode(argc, argv))
	{
		root = NULL;
		btree_insert_data(&root, (void *)(long)5, &h_cmp_int_asc);
		btree_insert_data(&root, (void *)(long)2, &h_cmp_int_asc);
		btree_insert_data(&root, (void *)(long)8, &h_cmp_int_asc);
		btree_insert_data(&root, (void *)(long)4, NULL);
		write(1, "OK\n", 3);
		return (0);
	}
	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	if (buffer[0] == 'M')
		cmpf = &h_cmp_int_mod10;
	else
		cmpf = &h_cmp_int_asc;
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
	root = NULL;
	i = 0;
	while (i < count)
	{
		btree_insert_data(&root, (void *)(long)values[i], cmpf);
		i++;
	}
	first = 1;
	print_prefix(root, &first);
	return (0);
}
