#ifndef HARNESS_UTILS_H
# define HARNESS_UTILS_H

# include "ft_btree.h"

# define H_TREE_NONE (-999999)

t_btree	*h_build_tree(int *values, int n);
void	h_put_int(int n);
int		h_cmp_int_asc(void *a, void *b);
int		h_cmp_int_mod10(void *a, void *b);
int		h_strcmp(char *s1, char *s2);
int		h_null_callback_mode(int argc, char **argv);

#endif
