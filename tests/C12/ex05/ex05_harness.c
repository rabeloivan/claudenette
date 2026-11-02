#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

t_list	*ft_list_push_strs(int size, char **strs);

int	main(void)
{
	char	buffer[4096];
	char	*strs[64];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	t_list	*list;
	t_list	*cur;

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
		strs[i] = buffer + pos;
		while (buffer[pos] != '\n' && buffer[pos] != '\0')
			pos++;
		buffer[pos] = '\0';
		pos++;
		i++;
	}
	list = ft_list_push_strs(count, strs);
	cur = list;
	i = 0;
	while (cur != NULL)
	{
		if (i > 0)
			write(1, "\x01", 1);
		h_put_str((char *)cur->data);
		cur = cur->next;
		i++;
	}
	return (0);
}
