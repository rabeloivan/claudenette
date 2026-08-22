/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ex03_harness.c                                     :+:      :+:    :+:   */
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

t_list	*ft_list_last(t_list *begin_list);

int	main(void)
{
	char	buffer[4096];
	int		bytes_read;
	int		count;
	int		pos;
	int		i;
	int		values[64];
	t_list	*list;
	t_list	*last;

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
	last = ft_list_last(list);
	if (last == NULL)
		write(1, "N", 1);
	else
	{
		write(1, "A", 1);
		h_put_int((int)(long)last->data);
	}
	return (0);
}
