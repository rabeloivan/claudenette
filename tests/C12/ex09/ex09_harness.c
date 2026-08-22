/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex09_harness.c                                     :+:      :+:    :+:   */
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

void	ft_list_foreach(t_list *begin_list, void (*f)(void *));

static int	g_count = 0;

static void	record(void *data)
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

	if (h_null_callback_mode(argc, argv))
	{
		values[0] = 1;
		values[1] = 2;
		values[2] = 3;
		list = h_build_list(values, 3);
		ft_list_foreach(list, NULL);
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
	ft_list_foreach(list, &record);
	return (0);
}
