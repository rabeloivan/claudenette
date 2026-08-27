#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_list	*ft_list_at(t_list *begin_list, unsigned int nbr);

int	main(void)
{
	char			buffer[4096];
	int				bytes_read;
	int				count;
	unsigned int	nbr;
	int				pos;
	int				i;
	int				values[64];
	t_list			*list;
	t_list			*elem;

	bytes_read = read(0, buffer, 4095);
	if (bytes_read < 0)
		return (0);
	buffer[bytes_read] = '\0';
	nbr = (unsigned int)atoi(buffer);
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
	elem = ft_list_at(list, nbr);
	if (elem == NULL)
		write(1, "N", 1);
	else
	{
		write(1, "A", 1);
		h_put_int((int)(long)elem->data);
	}
	return (0);
}
