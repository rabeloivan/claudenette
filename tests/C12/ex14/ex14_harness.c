#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

void	ft_list_sort(t_list **begin_list, int (*cmp)());

int	main(int argc, char **argv)
{
	char			buffer[4096];
	int				bytes_read;
	int				count;
	int				pos;
	int				i;
	int				values[64];
	t_list			*list;
	t_list			*cur;
	int				(*cmp)(void *, void *);

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 1;
		values[1] = 2;
		values[2] = 3;
		list = h_build_list(values, 3);
		ft_list_sort(&list, NULL);
		write(1, "OK\n", 3);
		return (0);
	}
	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	if (buffer[0] == 'D')
		cmp = &h_cmp_int_desc;
	else
		cmp = &h_cmp_int_asc;
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
	list = h_build_list(values, count);
	ft_list_sort(&list, cmp);
	cur = list;
	i = 0;
	while (cur != NULL)
	{
		if (i > 0)
			write(1, ",", 1);
		h_put_int((int)(long)cur->data);
		cur = cur->next;
		i++;
	}
	return (0);
}
