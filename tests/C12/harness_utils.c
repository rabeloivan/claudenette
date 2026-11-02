#include "harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_list	*h_build_list(int *values, int count)
{
	t_list	*list;
	t_list	*tail;
	t_list	*node;
	int		i;

	list = NULL;
	tail = NULL;
	i = 0;
	while (i < count)
	{
		node = (t_list *)malloc(sizeof(t_list));
		node->data = (void *)(long)values[i];
		node->next = NULL;
		if (tail == NULL)
			list = node;
		else
			tail->next = node;
		tail = node;
		i++;
	}
	return (list);
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

void	h_put_ptr(unsigned long n)
{
	char	c;

	if (n >= 10)
		h_put_ptr(n / 10);
	c = '0' + (n % 10);
	write(1, &c, 1);
}

void	h_put_str(char *s)
{
	while (*s)
		write(1, s++, 1);
}

int	h_strlen(char *s)
{
	int	i;

	i = 0;
	while (s[i] != '\0')
		i++;
	return (i);
}

int	h_strcmp(char *s1, char *s2)
{
	int	i;

	i = 0;
	while (s1[i] != '\0' && s1[i] == s2[i])
		i++;
	return ((unsigned char)s1[i] - (unsigned char)s2[i]);
}

int	h_cmp_int_asc(void *a, void *b)
{
	return ((int)(long)a - (int)(long)b);
}

int	h_cmp_int_desc(void *a, void *b)
{
	return ((int)(long)b - (int)(long)a);
}

int	h_cmp_str_asc(void *a, void *b)
{
	return (h_strcmp((char *)a, (char *)b));
}

int	h_cmp_str_desc(void *a, void *b)
{
	return (h_strcmp((char *)b, (char *)a));
}

int	h_null_callback_mode(int argc, char **argv)
{
	if (argc < 2)
		return (0);
	return (h_strcmp(argv[1], "nullcb") == 0);
}
