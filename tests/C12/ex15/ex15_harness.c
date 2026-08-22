/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex15_harness.c                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: rabeloivan <rabeloivan@student.42.fr>      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/16 00:00:00 by rabeloivan        #+#    #+#             */
/*   Updated: 2026/08/16 00:00:00 by rabeloivan       ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_list.h"
#include "../harness_utils.h"
#include <stdlib.h>
#include <unistd.h>

void	ft_list_reverse_fun(t_list *begin_list);

static void	print_walk(t_list *list)
{
	int	i;

	i = 0;
	while (list != NULL)
	{
		if (i > 0)
			write(1, ",", 1);
		h_put_ptr((unsigned long)list);
		write(1, ":", 1);
		h_put_int((int)(long)list->data);
		list = list->next;
		i++;
	}
}

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	int		values[64];
	t_list	*list;

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
	print_walk(list);
	write(1, "\n", 1);
	ft_list_reverse_fun(list);
	print_walk(list);
	return (0);
}
