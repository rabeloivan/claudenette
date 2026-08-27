#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_list	*ft_list_find(t_list *begin_list, void *data_ref, int (*cmp)());

int	main(int argc, char **argv)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		ref;
	int		pos;
	int		i;
	int		values[64];
	t_list	*list;
	t_list	*found;

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 1;
		values[1] = 2;
		values[2] = 3;
		list = h_build_list(values, 3);
		found = ft_list_find(list, (void *)(long)2, NULL);
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
	list = h_build_list(values, count);
	found = ft_list_find(list, (void *)(long)ref, &h_cmp_int_asc);
	if (found == NULL)
		write(1, "N", 1);
	else
	{
		write(1, "A", 1);
		h_put_int((int)(long)found->data);
	}
	return (0);
}
