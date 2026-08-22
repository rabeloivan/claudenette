#ifndef HARNESS_UTILS_H
# define HARNESS_UTILS_H

# include "ft_list.h"

t_list	*h_build_list(int *values, int count);
void	h_put_int(int n);
void	h_put_ptr(unsigned long n);
void	h_put_str(char *s);
int		h_strlen(char *s);
int		h_strcmp(char *s1, char *s2);
int		h_cmp_int_asc(void *a, void *b);
int		h_cmp_int_desc(void *a, void *b);
int		h_cmp_str_asc(void *a, void *b);
int		h_cmp_str_desc(void *a, void *b);
int		h_null_callback_mode(int argc, char **argv);

#endif
