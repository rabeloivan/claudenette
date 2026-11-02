#include "harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

static t_btree	*build_tree_rec(int *values, int n, int i)
{
	t_btree	*node;

	if (i >= n || values[i] == H_TREE_NONE)
		return (NULL);
	node = (t_btree *)malloc(sizeof(t_btree));
	node->item = (void *)(long)values[i];
	node->left = build_tree_rec(values, n, 2 * i + 1);
	node->right = build_tree_rec(values, n, 2 * i + 2);
	return (node);
}

t_btree	*h_build_tree(int *values, int n)
{
	return (build_tree_rec(values, n, 0));
}

void	h_put_int(int n)
{
	char	c;

	if (n < 0)
	{
		write(1, "-", 1);
		n = -n;
	}
	if (n >= 10)
		h_put_int(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

int	h_cmp_int_asc(void *a, void *b)
{
	return ((int)(long)a - (int)(long)b);
}

int	h_cmp_int_mod10(void *a, void *b)
{
	return (((int)(long)a % 10) - ((int)(long)b % 10));
}

int	h_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] != '\0' && s1[i] == s2[i])
		i++;
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}

int	h_null_callback_mode(int argc, char **argv)
{
	if (argc < 2)
		return (0);
	return (h_strcmp(argv[1], "nullcb") == 0);
}
