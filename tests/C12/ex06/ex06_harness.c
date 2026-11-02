#include "ft_list.h"
#include "../harness_utils.h"
#include "../../free_tracker.h"
#include <stdlib.h>
#include <unistd.h>

void	ft_list_clear(t_list *begin_list, void (*free_fct)(void *));

static int	g_count = 0;

static void	record_free(void *data)
{
	if (g_count > 0)
		write(1, ",", 1);
	h_put_int((int)(long)data);
	g_count++;
}

int	main(int argc, char **argv)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	int		values[64];
	t_list	*list;
	t_list	*node;

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 1;
		values[1] = 2;
		values[2] = 3;
		list = h_build_list(values, 3);
		ft_list_clear(list, NULL);
		write(1, "OK\n", 3);
		return (0);
	}
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
	list = h_build_list(values, count);
	node = list;
	while (node != NULL)
	{
		h_track(node);
		node = node->next;
	}
	ft_list_clear(list, &record_free);
	/*
	** The subject states two obligations - "removes and frees all links"
	** AND "free_fct is used to free each data". The comma-separated values
	** above cover only the second; without this line an implementation
	** that calls free_fct on every element and never frees a node scores
	** 100/100 while leaking the entire list.
	*/
	write(1, "\n", 1);
	h_put_str("nodes:freed=");
	h_put_int(h_freed_count());
	h_put_str(" leaked=");
	h_put_int(h_leaked_count());
	h_put_str(" double=");
	h_put_int(h_double_freed_count());
	write(1, "\n", 1);
	return (0);
}
