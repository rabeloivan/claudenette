/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex12_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_list.h"
#include "../harness_utils.h"
#include "../../free_tracker.h"
#include <stdlib.h>
#include <unistd.h>

void	ft_list_remove_if(t_list **begin_list, void *data_ref,
			int (*cmp)(), void (*free_fct)(void *));

static int	g_freed_count = 0;

static void	record_free(void *data)
{
	if (g_freed_count > 0)
		write(1, ",", 1);
	h_put_int((int)(long)data);
	g_freed_count++;
}

int	main(int argc, char **argv)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		ref;
	int		pos;
	int		i;
	int		values[64];
	int		node_vals[64];
	int		node_count;
	t_list	*list;
	t_list	*cur;
	t_list	*nodes[64];

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 1;
		values[1] = 2;
		values[2] = 3;
		list = h_build_list(values, 3);
		ft_list_remove_if(&list, (void *)(long)2, NULL, NULL);
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
	/*
	** Snapshot every link and its value before the call: afterwards the
	** removed ones have been freed and can't be dereferenced, but the
	** tracker can still be asked about their addresses. Without this the
	** harness only sees which `data` free_fct got and what's left in the
	** list - an implementation that unlinks nodes and frees their data but
	** leaks the nodes themselves looks identical to a correct one.
	*/
	i = 0;
	cur = list;
	while (cur != NULL && i < 64)
	{
		nodes[i] = cur;
		node_vals[i] = (int)(long)cur->data;
		h_track(cur);
		cur = cur->next;
		i++;
	}
	node_count = i;
	ft_list_remove_if(&list, (void *)(long)ref, &h_cmp_int_asc, &record_free);
	write(1, "\n", 1);
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
	/*
	** Per-link disposition, so the Python side can require exactly:
	** every link whose value matched data_ref was freed once ("F"), and
	** every link that stayed in the list was not freed at all ("K").
	** Freeing a retained link is a use-after-free, the opposite failure
	** from leaking a removed one, and both must be caught.
	*/
	write(1, "\n", 1);
	h_put_str("nodes:");
	i = 0;
	while (i < node_count)
	{
		if (i > 0)
			write(1, ",", 1);
		h_put_int(node_vals[i]);
		write(1, "=", 1);
		h_put_int(h_free_count_of(nodes[i]));
		i++;
	}
	write(1, "\n", 1);
	return (0);
}
